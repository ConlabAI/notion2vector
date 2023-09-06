import os
import logging
import json
import shutil
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from notion_client import Client, APIErrorCode, APIResponseError
from notion2md.exporter.block import MarkdownExporter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import NotionDirectoryLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.vectorstores import FAISS


def load_env_variables():

    load_dotenv()

    notion_token = os.environ.get('NOTION_TOKEN')
    notion_database_id = os.environ.get('NOTION_DATABASE_ID')
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    notion_database_query_filter_json = os.environ.get('NOTION_DATABASE_QUERY_FILTER')

    if not notion_token or not notion_database_id or not openai_api_key:
        logging.error("Essential environment variables are missing")
        exit(1)

    try:
        notion_database_query_filter = json.loads(notion_database_query_filter_json)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse NOTION_DATABASE_QUERY_FILTER: {e}")
        exit(1)

    return notion_token, notion_database_id, log_level, openai_api_key, notion_database_query_filter

def get_page_ids(notion_token, notion_database_id, log_level, notion_database_query_filter):
    logging.basicConfig(level=log_level)

    try:
        notion = Client(auth=notion_token, log_level=log_level)

        results = notion.databases.query(
            database_id=notion_database_id,
            filter=notion_database_query_filter
        )

        page_ids = [page['id'] for page in results["results"]]

        logging.info(f"Found {len(page_ids)} page IDs")
        return page_ids

    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            logging.error("Database not found. Please select a different database.")
        else:
            logging.error(error)
        return None
    
def export_pages_to_markdown(page_ids):
    output_path = 'notion_pages'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for block_id in page_ids:
        try:
            MarkdownExporter(block_id=block_id, output_path=output_path, download=False, unzipped=True).export()
            logging.info(f"Exported page {block_id} to markdown")
        except Exception as e:
            logging.error(f"Failed to export page {block_id}: {e}")

def process_documents_and_save_to_db():
    loader = NotionDirectoryLoader("notion_pages")
    persist_directory = 'faiss'

    docs = loader.load()

    headers_to_split_on = [
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    splits = []
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    for doc in docs:
        markdown_document = doc.page_content
        doc_splits = markdown_splitter.split_text(markdown_document)
        for split_doc in doc_splits:
            merged_metadata = {**doc.metadata, **split_doc.metadata}  # Merge the two dictionaries
            split_doc.metadata = merged_metadata  # Update the split document's metadata

        splits.extend(doc_splits)

    embeddings = OpenAIEmbeddings()

    vectorstore = FAISS(persist_directory=persist_directory, embedding_function=embeddings)

    try:
        # Fetch all document IDs from the collection
        all_documents = vectorstore.get()
        if 'ids' in all_documents and all_documents['ids']:
                all_ids = all_documents['ids']
                vectorstore.delete(ids=all_ids)
                logging.info(f"All documents deleted from vector store")
        else:
            logging.info(f"Vector store is empty")
    except Exception as e:
            logging.error(f"Failed to delete all documents from collection: {e}")
            exit(1)

    try:      
        vectorstore.add_documents(splits)
        logging.info(f"All documents added to vector store")
    except Exception as e:
        logging.error(f"Failed to create vector store from documents: {e}")
        exit(1)

def ingest_data():
    notion_token, notion_database_id, log_level, openai_api_key, notion_database_query_filter = load_env_variables()
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    if log_level not in log_levels:
        logging.error(f"Invalid LOG_LEVEL value. Choose from {log_levels}")
        exit(1)

    logging.basicConfig(level=log_level)

    page_ids = get_page_ids(notion_token, notion_database_id, log_level, notion_database_query_filter)

    if page_ids:
        export_pages_to_markdown(page_ids)
        process_documents_and_save_to_db() # Added this function to process and save the documents

app = FastAPI()

@app.get("/ingest")
def ingest():
    ingest_data()
    return {"status": "ingestion completed"}

if __name__ == "__main__":
    ingest_data()
    uvicorn.run(app, host="0.0.0.0", port=80)
