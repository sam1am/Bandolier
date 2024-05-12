import requests

def main():
    while True:
        query_text = input("Enter your query (or 'q' to quit): ")
        
        if query_text.lower() == 'q':
            break
        
        # Send the query to the API endpoint
        response = requests.post('http://localhost:5000/api/query', json={'query': query_text})
        
        if response.status_code == 200:
            data = response.json()
            short_answer = data.get('short_answer')
            
            if short_answer:
                print("Short Answer:")
                print(short_answer)
            else:
                print("No short answer available.")
        else:
            print("Error occurred while processing the query.")

if __name__ == "__main__":
    main()