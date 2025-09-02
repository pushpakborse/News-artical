from rag_system import RAGSystem

def main():
    try:
        # Initialize RAG system
        rag = RAGSystem()
        
        # Let user select sources
        rag.select_sources()
        
        # Load news articles from selected sources
        if not rag.load_news():
            return
        
        print("\n" + "="*60)
        print("NEWS RAG SYSTEM (Terminal Mode)")
        print("For clickable citations, run: streamlit run app_simple.py")
        print("="*60)
        print("Type 'quit' or 'exit' to stop\n")
        
        while True:
            question = input("Your question (or 'open X' to open citation): ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Handle citation opening
            if question.lower().startswith('open '):
                try:
                    import webbrowser
                    citation_num = question.split()[1]
                    if hasattr(rag, 'last_citations') and rag.last_citations and citation_num in rag.last_citations:
                        url = rag.last_citations[citation_num]
                        print(f"Opening citation [{citation_num}]: {url}")
                        webbrowser.open(url)
                    else:
                        print(f"Citation [{citation_num}] not found. Available: {list(rag.last_citations.keys()) if hasattr(rag, 'last_citations') and rag.last_citations else 'None'}")
                except (ValueError, IndexError):
                    print("Usage: open <number> (e.g., 'open 1')")
                continue
            
            if not question:
                continue
            
            print("\nThinking...")
            result = rag.query(question)
            
            if isinstance(result, dict):
                print("\n" + "="*60)
                print("ANSWER:")
                print("="*60)
                
                # Process answer to make citations clickable
                answer_text = result['answer']
                if 'citations' in result and result['citations']:
                    import re
                    # Find all [1], [2], [3] etc. in the answer
                    citation_pattern = r'\[(\d+)\]'
                    
                    def make_clickable(match):
                        num = match.group(1)
                        if num in result['citations']:
                            url = result['citations'][num]
                            return f"\033]8;;{url}\033\\[{num}]\033]8;;\033\\"
                        return match.group(0)
                    
                    answer_text = re.sub(citation_pattern, make_clickable, answer_text)
                
                print(answer_text)
                
                # Add manual citation opening option
                if 'citations' in result and result['citations']:
                    print(f"\n💡 Click on [1], [2] etc. above or type 'open 1', 'open 2' to open sources")
                
                print(f"\n📊 Used {result['context_used']} relevant chunks from {len(result['sources'])} sources")
            else:
                print("\n" + "="*60)
                print("ANSWER:")
                print("="*60)
                print(f"{result}")
            
            print("\n" + "="*60 + "\n")
    
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set your GEMINI_API_KEY in the .env file")

if __name__ == "__main__":
    main()