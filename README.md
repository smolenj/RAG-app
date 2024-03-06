# Group 11 - QAsystem-INLPT-WS2023

Repository with our project for NLP with Transformers course. 





### Final project report: [documentation.md](https://github.com/mstaczek/QAsystem-INLPT-WS2023/blob/main/documentation.md)

## Note - This repo uses Git LFS for CSV files

1. Install: https://git-lfs.com/
2. Run `git lfs install`
3. Afterwards, git will automatically download large CSV files from LFS and when adding them to the repository, they will be stored somewhat separately from regular files.

---

# Introduction - chatMaJA
The project focuses on developing a question-answering machine using Large Language Models (LLM) wherein data from PubMed is used containing the keyword "Intelligence" ranging from the year 2013-2023. 

Example of our Gradio UI, streaming model output to the user:

![GIF of Gradio](/img/Gradio.gif)

# Goal
The objective of developing this project is to understand how these LLMs can nowadays be used, to help solve problems of question-answering domain-specific systems.

# [Meeting Notes](/Meetings)
The creators of this project gather and contribute their regular research and learnings to further understand the process and discuss the current and next phases of this project.

# Directory structure:
- `Evaluation` - all files needed to perform an evaluation of the solution and the results of it,
- `Final_solution` - all files needed to run the final version of our solution,
- `Meetings` - meeting notes,
- `Previous_Work` - all files created during previous phases of the project,
- `img` - all images used in the documentation file,
- `presentation_milestone_1.pdf` - file with the presentation we created for milestone 1,
- `documentation.md` - report.

# How to run the project?

All files needed to run our solution can be found in the directory `Final_Solution`. The requirements regarding packages are in the `Final_Solution\requirements.txt` file. In the folder `Final_Solution` there is also a detailed description, of how to run each part of the solution and why.

In general, the final version of our solution includes two UIs, which can be used following the steps from the description below.

## Local Docker + simple Flask (CPU)

This version of UI works on CPU only and is easily available by building and running a standalone Docker container. Below there is a screenshot of working UI. The detailed description about the Docker container can be found in README.md in directory `Docker_Flask_App`.

![Screenshot of UI with sources](/img/Flask_UI.png)

### How to run - with Docker Compose

> **Note:** commands below assume you're in the directory `QAsystem-INLPT-WS2023/Final_Solution/Docker_Flask_App` with the `Dockerfile.base`, `Dockerfile` and `docker-compose.yaml` files.

Build an image with the environment and run docker compose up (which automatically will build an image with the app):

```bash
docker build -t chatmaja_base:v1 -f Dockerfile.base .
docker compose up
```

Then, open http://localhost:5000/. 

#### Two version of CSV files

We prepared 2 datasets - one with chunks from 100 abstracts, and the other with chunks from all abstracts. Loading all chunks to LanceDB requires computing embeddings and takes a very long time on CPU (but works). Either run on a tiny subset of data or download a ready database.

> Options:
> > Update `docker-compose.yml` to use a smaller dataset.
> 
> OR
> 
> > Download and extract a ready LanceDB database `db` folder and place it in the same directory as `docker-compose.yml` - [download link](https://wutwaw-my.sharepoint.com/:f:/g/personal/01151437_pw_edu_pl/EnwtlXrMPApNlDmptSaLnQEBYF_-Bxe7xUs47pqBqQhBYg?e=DCKSDy).

> **For best answers, use all abstracts and download the precomputed LanceDB database.**

>Note: read the readme in `QAsystem-INLPT-WS2023/Final_Solution/Docker_Flask_App` to learn, how to download and add precomputed LanceDB embeddings.

## Gradio notebook (with GPU, on Colab too) - recommended

For better performance and user experience, use UI variant with Gradio in Jupyter Notebook (can be run on Collab with GPU):

Below there is a screenshot of working UI, opened in a separate browser card:

![Screenshot of Gradio](/img/Gradio.png)

and a screenshot of Gradio directly in Colab, with T4 GPU:

![Screenshot of Gradio in Colab](/img/Gradio_Colab.png)


### How to run - Gradio notebook

Simply open the Jupyter notebook `notebook_with_gradio.ipynb` in the `Final_Solution` folder and run all cells. The Gradio UI will be available both in Jupyter Notebook and at http://localhost:7860/.

To run on Colab, you need to upload requirements:
- `QAsystem-INLPT-WS2023\Final_Solution\requirements.txt`

and data, either the whole dataset or a sample:

- sample:  `QAsystem-INLPT-WS2023\Final_Solution\data\preprocessed_data\master_without_embeddings_first_100.csv`,
- whole: `QAsystem-INLPT-WS2023\Final_Solution\data\preprocessed_data\master_without_embeddings_all.csv`.

Remember to set the correct paths to those files (in first cell to install all requirements and later, set `path_to_data_csv` to point to the CSV file).

The Gradio UI will be available both in Colab, and at a printed URL.

#### Gradio - download precomputed LanceDB embeddings

Loading whole dataset to LanceDB takes more than 5 minutes on T4 Colab GPU. We provide a ready LanceDB database `db` folder to download. Extract it to create a folder `db` in the same directory as `notebook_with_gradio.ipynb` - [download link](https://wutwaw-my.sharepoint.com/:f:/g/personal/01151437_pw_edu_pl/EnwtlXrMPApNlDmptSaLnQEBYF_-Bxe7xUs47pqBqQhBYg?e=DCKSDy).

> **For best answers, use all abstracts and download the precomputed LanceDB database.**

--------------------------------
