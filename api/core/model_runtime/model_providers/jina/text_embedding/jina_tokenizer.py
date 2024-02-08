from os.path import abspath, dirname, join


class JinaTokenizer:
    @staticmethod
    def _get_num_tokens_by_jina_base(text: str) -> int:
        """
            use jina tokenizer to get num tokens
        """
        base_path = abspath(__file__)
        gpt2_tokenizer_path = join(dirname(base_path), 'tokenizer')
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(gpt2_tokenizer_path)
        tokens = tokenizer.encode(text)
        return len(tokens)
    
    @staticmethod
    def get_num_tokens(text: str) -> int:
        return JinaTokenizer._get_num_tokens_by_jina_base(text)