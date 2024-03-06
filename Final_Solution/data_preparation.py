import os
import pandas as pd
from transformers import AutoTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import copy

# Set constants
number_of_first_rows = 100 # set to -1 to process all data
batch_size = 100
chunk_size=400
chunk_overlap=50

# Directory containing your .xlsx files
directory_path = 'data/raw_data'

# Output CSV file path
path = "data/preprocessed_data"
if not os.path.exists(path):
    os.mkdir(path)
if number_of_first_rows == -1:
    output_csv_path = f'data/preprocessed_data/master_without_embeddings_all.csv'
else:
    output_csv_path = f'data/preprocessed_data/master_without_embeddings_first_{number_of_first_rows}.csv'

# Initialize an empty DataFrame to store the extracted data
result_df = pd.DataFrame(columns=['PMID', 'Title', 'Abstract', 'Author(s)', 'Source'])

# Loop through each file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".xlsx"):
        file_path = os.path.join(directory_path, filename)

        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path)

        # Extract relevant columns ('PMID', 'Title', 'Abstract', 'Source', 'Author(s)') and append to the result DataFrame
        result_df = pd.concat([result_df, df[['PMID', 'Title', 'Abstract', 'Source', 'Author(s)']]])

# Load tokenizer
llama_model_name = 'meta-llama/Llama-2-7b-chat-hf'
tokenizer = AutoTokenizer.from_pretrained(llama_model_name, token='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')

# Read the CSV file into a DataFrame
master_df = copy.deepcopy(result_df)
master_df = master_df[:number_of_first_rows]

new_df = pd.DataFrame(columns=['id', 'title', 'chunk', 'authors', 'sources'])

def token_len(text):
    tokens = tokenizer.encode(text)
    return len(tokens)

# Process abstracts in batches
for i in range(0, len(master_df), batch_size):
    batch_df = master_df.iloc[i:i+batch_size]
    if i%50:
        print(f"Batch number: {i+1}.")

    chunks = []
    new_ids = []
    titles = []
    sources = []
    authors = []
    # Process each abstract in batch
    for idx, row in batch_df.iterrows():
        title = row['Title']
        author = row['Author(s)'] 
        abstract_sentences = row['Abstract']
        
        #chunking
        text_splitter = RecursiveCharacterTextSplitter(
                                                        chunk_size=chunk_size,
                                                        chunk_overlap=chunk_overlap,
                                                        length_function=token_len,
                                                        separators=['\n\n', '\n', ' ', '']
                                                    )
        abstract_chunks = text_splitter.split_text(abstract_sentences)

        for chunk_number, chunk in enumerate(abstract_chunks):
            new_id = f'{row["PMID"]}_{chunk_number + 1}' 
            source = f"https://pubmed.ncbi.nlm.nih.gov/{row['PMID']}/"
            chunks.append(chunk)
            new_ids.append(new_id)
            titles.append(title)
            sources.append(source)
            authors.append(author)
            
    # Add new data
    new_df = pd.concat([new_df, pd.DataFrame({'id':new_ids, 'title':titles, 'chunk':chunks, 
                                         'authors':authors,
                                         'sources': sources})])
    
    # Clear variables to free up memory
    del batch_df, chunks, new_ids

# Write the updated master DataFrame to a single CSV file
new_df.to_csv(output_csv_path, index=False)

print(f"Data extracted and saved to {output_csv_path}")