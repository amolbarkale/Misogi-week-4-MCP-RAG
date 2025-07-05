import re
def smart_chunk_document(text: str, chunk_size: int = 800, overlap: int = 100) -> List[Dict]:
  """
  Split document into chunks with intelligent boundaries
  Args:
    text: Document text to chunk
    chunk_size: Target size for each chunk (characters)
    overlap: Overlap between chunks (characters)
  Returns:
    List of chunk dictionaries with text and metadata
  """
  chunks = []
  current_chunk = ""
  # Step 1: Split by paragraphs (natural boundaries)
  paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
  for paragraph in paragraphs:
    # Step 2: Handle long paragraphs by splitting into sentences
    if len(paragraph) > chunk_size:
      # Split long paragraph into sentences
      sentences = split_into_sentences(paragraph)
      # Process each sentence
      for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
          # Save current chunk and start new one
          chunks.append(create_chunk_dict(current_chunk, chunks))
          current_chunk = create_smart_overlap(current_chunk, overlap) + sentence
        else:
          # Add sentence to current chunk
          current_chunk = add_text_to_chunk(current_chunk, sentence, separator=' ')
    else:
      # Step 3: Handle normal paragraphs
      if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
        # Save current chunk and start new one
        chunks.append(create_chunk_dict(current_chunk, chunks))
        current_chunk = create_smart_overlap(current_chunk, overlap)
        current_chunk = add_text_to_chunk(current_chunk, paragraph, separator='\n\n')
      else:
        # Add paragraph to current chunk
        current_chunk = add_text_to_chunk(current_chunk, paragraph, separator='\n\n')
  # Step 4: Add final chunk if it exists
  if current_chunk.strip():
    chunks.append(create_chunk_dict(current_chunk, chunks))
  return chunks
def split_into_sentences(text: str) -> List[str]:
  """Split text into sentences, keeping punctuation"""
  sentences = re.split(r'(?<=[.!?])\s+', text)
  return [s.strip() for s in sentences if s.strip()]
def create_smart_overlap(current_chunk: str, overlap_size: int) -> str:
  """Create overlap that preserves sentence boundaries"""
  if overlap_size <= 0 or len(current_chunk) <= overlap_size:
    return ""
  # Take last 'overlap_size' characters
  overlap_text = current_chunk[-overlap_size:].strip()
  # Find good boundary after sentence-ending punctuation
  for punct in ['.', '!', '?', ';', ':']:
    last_punct = overlap_text.rfind(punct)
    if last_punct > 0:
      # Start overlap after the punctuation
      return overlap_text[last_punct+1:].strip()
  # Fallback: break at word boundary
  first_space = overlap_text.find(' ')
  if first_space > 0:
    return overlap_text[first_space:].strip()
  return overlap_text
def add_text_to_chunk(current_chunk: str, new_text: str, separator: str) -> str:
  """Add new text to chunk with appropriate separator"""
  if current_chunk:
    return current_chunk + separator + new_text
  return new_text
def create_chunk_dict(chunk_text: str, existing_chunks: List[Dict]) -> Dict:
  """Create standardized chunk dictionary"""
  clean_text = chunk_text.strip()
  return {
    'text': clean_text,
    'length': len(clean_text),
    'start_pos': sum(len(c['text']) for c in existing_chunks)
  }