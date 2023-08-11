# Notion to Vector Database Loader

## Description

This project's goal is to automatically load data from a Notion database into a vector database. It includes functionality to query Notion databases, convert pages to Markdown, split by headers, and process splits into vectorized formats. It's particularly useful for applications that require embedded representations of text.

### :warning: Caution :warning:

This project is currently under development and not suitable for production use. Please note that the vector database resets after each restart.

## Features

- **Environment Variables:** Manage configurations via environment variables.
- **Notion Database Querying:** Fetch page IDs from a specified Notion database.
- **Markdown Export:** Convert Notion pages to Markdown files.
- **Text Splitting:** Break down documents into manageable sections.
- **Embedding Generation:** Generate embeddings for textual content.
- **Vector Database Management:** Process and save documents in the vector database (Chroma).
- **API Endpoint:** Trigger ingestion through the `/ingest` API endpoint.

## Installation

1. Clone this repository.
2. Install dependencies:
   \```bash
   pip install -r requirements.txt
   \```

## Usage

You need to set the following environment variables:

- `NOTION_TOKEN`: Notion token for authentication.
- `NOTION_DATABASE_ID`: ID of the Notion database.
- `LOG_LEVEL`: Log level (optional, default 'INFO').
- `OPENAI_API_KEY`: OpenAI API key.
- `NOTION_DATABASE_QUERY_FILTER`: JSON filter for querying the Notion database.

## Configuration

The application uses environment variables for configuration. You'll find a template for these variables in the `.env.example` file.

### Step 1: Copy the Example Environment File

Copy the `.env.example` file to a new file named `.env`:

\```bash
cp .env.example .env
\```

### Step 2: Edit the Variables

Open the `.env` file in a text editor and update the values to match your configuration:


## Running local

After setting these variables, run the script with:

\```bash
python notion2vector/main.py
\```

## Running with Docker

You can build the Docker image and run the container using the following commands:

\```bash
docker build -t notion2vector .
docker run -p 4000:80 --env-file .env notion2vector 
\```

Once the application is running, it will automatically load the Notion database into the vector database. You can re-trigger the ingestion process by sending a POST request to the `/ingest` endpoint:

\```bash
curl -X POST http://localhost:4000/ingest
\```

## Using with Other Applications

To use the vector database with other applications, you need to create a Docker persistent volume for the `chroma_db` directory. This ensures that the data remains available between container restarts and can be shared with other containers.

Here's how to set it up:

### Step 1: Create a Persistent Volume

Create a volume using Docker:

\```bash
docker volume create --name=chroma_db_volume
\```

### Step 2: Run the Container with Volume Mounted

When running the container, you need to mount the volume to the `chroma_db` directory inside the container:

\```bash
docker run -p 4000:80 --env-file .env -v chroma_db_volume:/app/chroma_db notion2vector
\```

### Step 3: Mount the Volume with Other Containers

You can now mount this volume in other containers that need to query the Chroma DB. Simply use the same volume name and mount it to the appropriate path within the other container:

\```bash
docker run -v chroma_db_volume:/path/in/other/container other-image-name
\```

Replace `/path/in/other/container` with the appropriate path inside the other container where you want the Chroma DB data to be accessible.

### Note

Make sure the application is configured correctly to use the `chroma_db` directory for storing the vector data, and the directory permissions are set appropriately for the container user.

## To Do

- Pagges content clean up.
- Process only updated pages.
- Remove Langchain dependency.
- Add more settings for MD spliting.
- Expose Chroma DB API.

## Support & Contribution

Feel free to open issues or submit pull requests if you find any bugs or have suggestions for improvements.

## License

[MIT]