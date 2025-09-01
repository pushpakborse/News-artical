from rag_system import RAGSystem

def main():
    try:
        # Initialize RAG system
        rag = RAGSystem()
        
        # Load news articles
        if not rag.load_news():
            return
        
        print("\n" + "="*50)
        print("NEWS RAG SYSTEM - Ask questions about current news")
        print("="*50)
        print("Type 'quit' or 'exit' to stop\n")
        
        while True:
            question = input("Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print("\nThinking...")
            result = rag.query(question)
            
            if isinstance(result, dict):
                print("\n" + "="*60)
                print("ANSWER:")
                print("="*60)
                print(f"{result['answer']}")
                print("\n" + "="*60)
                print(f"SOURCES ({len(result['sources'])}):")
                print("="*60)
                for i, source in enumerate(result['sources'], 1):
                    print(f"{i}. {source}")
                print(f"\n📊 Used {result['context_used']} relevant chunks from the database")
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