# taken and copied from https://github.com/OpenNMT/OpenNMT-tf/blob/master/config/models/transformer_shared_embedding.py
"""A Transformer model sharing all embeddings and softmax weights."""

import tensorflow as tf
import opennmt as onmt

def model():
  return onmt.models.Transformer(
	source_inputter=onmt.inputters.WordEmbedder(
		vocabulary_file_key="source_words_vocabulary",
		embedding_size=300),
	target_inputter=onmt.inputters.WordEmbedder(
          vocabulary_file_key="target_words_vocabulary",
          embedding_size=300),
    num_layers=2,
    num_units=256,
    num_heads=4,
    ffn_inner_dim=1024,
    dropout=0.1,
    attention_dropout=0.1,
    relu_dropout=0.1,
    share_embeddings=onmt.models.EmbeddingsSharingLevel.ALL)
