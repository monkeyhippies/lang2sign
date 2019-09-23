data:
	./utils/download_en_asl_gloss_data.sh
preprocess:
	python utils/preprocess_en_asl_gloss_data.py \
		--min_vocab_count 15 \
		--embedding_file=pretrained-embeddings/glove.6B.300d.txt \
		--train_files=data/raw/lang2gloss/enasl/train/ENG-ASL_Train_0.046.en,data/raw/lang2gloss/enasl/train/ENG-ASL_Train_0.046.asl \
		--test_files=data/raw/lang2gloss/enasl/test/ENG-ASL_Test_0.046.en,data/raw/lang2gloss/enasl/test/ENG-ASL_Test_0.046.asl \
		--dev_files=data/raw/lang2gloss/enasl/dev/ENG-ASL_Dev_0.046.en,data/raw/lang2gloss/enasl/dev/ENG-ASL_Dev_0.046.asl
pretrained-embeddings:
	./utils/download_glove_embeddings.sh
