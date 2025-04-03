from domain.paper import Paper

if __name__ == "__main__":
    file_path = "sample_papers/example1.pdf"
    paper = Paper.from_pdf(file_path)

    print("\n✅ Paper Loaded!")
    print("Title:", paper.title)
    print("Authors:", paper.authors)
    print("Abstract:", paper.abstract)
    print("\n--- First 500 characters of paper ---\n")
    print(paper.raw_text[:500])
