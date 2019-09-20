.PHONY: data

data:
	./utils/download_en_asl_gloss_data.sh
word-embeddings:
	./utils/download_glove_embeddings.sh
