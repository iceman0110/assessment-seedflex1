# StatementSense AI API

This project is an AI-powered API that processes a `.zip` file of PDF bank statements. It uses a robust, decoupled architecture built with FastAPI and LangGraph to extract financial data, handle errors gracefully, and return a single JSON summary.

## 🚀 Project Architecture

This project uses a clean, decoupled architecture to separate responsibilities, making it maintainable and testable.

### File Structure & Roles

Here is the file structure and the role each file/folder plays:

```
.
├── main.py                 # 1. The API Layer & Composition Root
├── schemas.py              # 2. The Data Layer (Pydantic Models)
│
├── interfaces/services/    # 3. The "Contracts" (Abstract Interfaces)
│   ├── IPDFLoader.py
│   └── IAIExtractor.py
│
├── services/               # 4. The "Tools" (Concrete Implementations)
│   ├── PDFLoader.py
│   └── AIExtractor.py
│
├── graph/                  # 5. The "Factory" (Core Logic)
│   ├── state.py            # - The "Tote Bin" (GraphState)
│   ├── nodes.py            # - The "Stations" (load_pdf, extract_data)
│   ├── workflow.py         # - The "Assembly Line" (GraphWorkflow)
│   └── processor.py        # - The "Factory Operator"
│
├── .env                    # App configuration and API keys
├── requirements.txt        # Project dependencies
└── README.md               # You are here!
```

### Explanation of Roles

1.  **`main.py` (API Layer & Composition Root):**
    On startup, it builds all the objects (injecting `PdfLoaderService` into `nodes`, `nodes` into `workflow`, etc.) and creates the final `StatementProcessor`. At runtime, it just hosts the API endpoint.

2.  **`schemas.py` (Data Layer):**
    Defines all Pydantic models (e.g., `BankStatement`, `APIResponse`) that describe our data.

3.  **`interfaces/services/` (The "Contracts"):**
    Defines the abstract base classes for our tools. The core logic depends on these, not on specific libraries.

4.  **`services/` (The "Tools"):**
    The "dirty" code. These classes implement the interfaces using real libraries (e.g., `PdfLoaderService` uses `pypdf`).

5.  **`graph/` (The "Factory"):**
    This is the core of the application logic.

      * **`graph/state.py`**: Defines the "memory" (`GraphState`) that moves between nodes.
      * **`graph/nodes.py`**: Defines the "stations" (`load_pdf`, `extract_data`) that depend on the interfaces.
      * **`graph/workflow.py`**: The `GraphWorkflow` class that "wires" the nodes and edges together.
      * **`graph/processor.py`**: The "factory operator." This class handles the business logic (unzipping, looping) and uses the compiled graph to process each file.

-----

## ⚙️ How it Works: LangGraph & Error Handling

The key requirement is that **one bad file must not crash the entire process**. We use LangGraph to manage this.

The `StatementProcessor` unzips the file and loops through each PDF. For *each* PDF, it invokes the compiled LangGraph workflow. This workflow (defined in `graph/workflow.py`) has a conditional edge that is key for error handling.

### The Workflow for One PDF:

1.  **`load_pdf` (Node)**: The `PdfLoaderService` tries to extract text.

      * **Success**: It puts the text into the `GraphState` and proceeds.
      * **Failure** (e.g., corrupted file or image-only PDF): It puts an **error message** into the `GraphState`.

2.  **`should_continue` (Edge)**: The graph checks the state.

      * If an `error` exists, it **routes the flow directly to the `finalize_result` node**.
      * It completely **skips** the `extract_data` (LLM) node.

3.  **`extract_data` (Node)**: This only runs if the PDF was loaded correctly. It calls the LLM.

      * **Failure** (e.g., bad API key): It puts an `error` into the `GraphState`.

4.  **`finalize_result` (Node)**: This final node runs no matter what. It checks the state and formats either a `FileProcessSuccess` or `FileProcessFail` object.

This design ensures we never send a bad PDF to the LLM (saving API costs) and that every file is accounted for in the final JSON, even if it fails.

-----

## 🏁 How to Set Up and Run

### 1\. Project Setup

1.  **Clone the repository:**

    ```bash
    git clone [your-repo-link]
    cd [your-project-folder]
    ```

2.  **Create a virtual environment:**

3.  **Install dependencies:**
    Create a `requirements.txt` file (if you don't have one) with the content below, then run `pip install -r requirements.txt`.


4.  **Create your `.env` file:**
    In the root folder, create a `.env` file. This tells the app *which* AI to use and provides the keys.

    **`.env`**

    ```ini
    # Specify which provider your app should use: "google" or "openai"
    AI_PROVIDER="google"

    # --- API Keys ---
    GOOGLE_API_KEY="AIzaSy..."
    OPENAI_API_KEY="sk-..."
    ```

### 2\. Run the Server

With your virtual environment active, run the FastAPI server:

```bash
uvicorn main:app --reload
```

Your API is now running locally at `http://127.0.0.1:8000`.

-----

## 🌐 Exposing with Ngrok

To let others test your API, you must expose your local server to the internet.

1.  **Download Ngrok:** Go to the [ngrok dashboard](https://dashboard.ngrok.com/signup), sign up, and download the `ngrok.exe` file. Place it in your project folder or a folder in your system's PATH.

2.  **Add Auth Token:** Run the command they provide to link your account. You only need to do this once.

    ```bash
    ngrok config add-authtoken <YOUR_TOKEN_HERE>
    ```

3.  **Run Your Server (Terminal 1):** In your first terminal, make sure your FastAPI app is running:

    ```bash
    uvicorn main:app
    ```

4.  **Run Ngrok (Terminal 2):** Open a **new, separate terminal** (or a new tab in your Windows Terminal) and tell ngrok to forward your local port 8000.

    ```bash
    ngrok http 8000
    ```

5.  **Get Your URL:** Ngrok will show you a public "Forwarding" URL. This is your new public API address.

    ```
    Forwarding                    [https://some-random-string.ngrok-free.app](https://some-random-string.ngrok-free.app) -> http://localhost:8000
    ```

-----

## 🧪 How to Test

You can't test a file upload API by just visiting the URL in a browser. Use the built-in FastAPI documentation.

1.  Take your public `ngrok` URL and add `/docs` to the end.

    > **Example:** `https://some-random-string.ngrok-free.app/docs`

2.  Open this URL in your browser. You will see the FastAPI interactive API documentation.

3.  Find the `POST /process-statements/` endpoint and click to expand it.

4.  Click the **"Try it out"** button.

5.  Under "file", click **"Choose File"** and upload your sample `.zip` file of bank statements.

6.  Click the **"Execute"** button.

7.  Scroll down to the "Response" section to see the full JSON output summarizing your processed files.
