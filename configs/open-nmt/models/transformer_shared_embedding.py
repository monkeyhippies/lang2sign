# taken and copied from https://github.com/OpenNMT/OpenNMT-tf/blob/master/config/models/transformer_shared_embedding.py
"""A Transformer model sharing all embeddings and softmax weights."""
import opennmt as onmt

def model():
    return onmt.models.Transformer(
        source_inputter=onmt.inputters.WordEmbedder(
            embedding_size=300),
        target_inputter=onmt.inputters.WordEmbedder(
            embedding_size=300),
    num_layers=6,
    num_units=300,
    num_heads=6,
    ffn_inner_dim=2048,
    dropout=0.1,
    attention_dropout=0.1,
    relu_dropout=0.1,
    share_embeddings=onmt.models.EmbeddingsSharingLevel.ALL)
