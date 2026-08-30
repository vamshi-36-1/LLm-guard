"""
LLM-Guard: Embedding Extractor
Person 2 (AI/Security Lead) - Week 1
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from pathlib import Path
import time

class EmbeddingExtractor:
    """Extract embeddings from prompts using sentence-transformers"""
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize with lightweight embedding model
        
        Model specs:
        - Fast: 50ms per prompt
        - Compact: 384 dimensions
        - Small: 22MB memory footprint
        - Quality: Good for classification tasks
        """
        print(f"🤖 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = 384
        print(f"✅ Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def encode_batch(self, texts, batch_size=32):
        """
        Encode list of prompts to embeddings
        
        Args:
            texts: List of prompt strings
            batch_size: Number of prompts to process at once
        
        Returns:
            embeddings: NumPy array of shape (len(texts), 384)
        """
        print(f"📝 Encoding {len(texts)} prompts (batch size: {batch_size})...")
        start_time = time.time()
        
        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=True)
        
        elapsed = time.time() - start_time
        avg_time = (elapsed / len(texts)) * 1000  # ms per prompt
        
        print(f"⏱️  Total time: {elapsed:.1f}s ({avg_time:.1f}ms per prompt)")
        return embeddings
    
    def process_dataset(self, input_path, output_path):
        """
        Load dataset, extract embeddings, save to CSV
        
        Args:
            input_path: Path to prompts_combined.csv
            output_path: Path to save embeddings
        """
        print(f"\n📖 Loading dataset from {input_path}")
        df = pd.read_csv(input_path)
        
        print(f"   Found {len(df)} prompts")
        print(f"   Columns: {df.columns.tolist()}")
        
        # Extract embeddings
        embeddings = self.encode_batch(df['prompt'].tolist())
        
        # Store embeddings as CSV (embedding column is a list of floats)
        df['embedding'] = [list(emb) for emb in embeddings]
        df.to_csv(output_path, index=False)
        
        print(f"\n✅ Saved {len(df)} embeddings to {output_path}")
        print(f"   Embedding shape: ({len(embeddings)}, {len(embeddings[0])})")
        
        # Show stats
        print(f"\n📊 Embedding statistics:")
        all_embeddings = np.array(embeddings)
        print(f"   Min value: {all_embeddings.min():.4f}")
        print(f"   Max value: {all_embeddings.max():.4f}")
        print(f"   Mean value: {all_embeddings.mean():.4f}")
        print(f"   Std dev: {all_embeddings.std():.4f}")
        
        return df
    
    def load_embeddings(self, embeddings_path):
        """Load pre-computed embeddings from CSV"""
        df = pd.read_csv(embeddings_path)
        embeddings = np.array([eval(e) for e in df['embedding']])
        return embeddings, df

if __name__ == "__main__":
    print("=" * 60)
    print("LLM-Guard: Embedding Extractor")
    print("=" * 60 + "\n")
    
    # Create output directory
    output_dir = Path('data/processed')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract embeddings
    extractor = EmbeddingExtractor()
    
    df = extractor.process_dataset(
        input_path='data/raw/prompts_combined.csv',
        output_path='data/processed/prompts_embedded.csv'
    )
    
    print("\n📋 Sample embedding (first 10 dimensions):")
    embedding = [float(x) for x in df['embedding'].iloc[0]]
    print(f"   {embedding[:10]}")
    
    print("\n✅ Embedding extraction complete! Ready for training.")
