from huggingface_hub import HfApi

api = HfApi()

repo_id = "TheBloke/GPT4All-J-Groovy-GGUF"

files = api.list_repo_files(repo_id)

print(f"Archivos en el repositorio {repo_id}:")
for file in files:
    print(file)
