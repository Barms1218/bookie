import 'package:flutter/material.dart';
import '../models/book.dart';
import 'package:frontend/services/book_service.dart';

class BookSearchPage extends StatefulWidget {
  const BookSearchPage({super.key});

  @override
  State<BookSearchPage> createState() => _BookSearchPageState();
}

class _BookSearchPageState extends State<BookSearchPage> {
  final BookService _bookService = BookService();

  final TextEditingController _searchController = TextEditingController();

  Future<List<BookSearchResult>>? _searchResults;

  void _performSearch() {
    setState(() {
      _searchResults = _bookService.searchBooks(_searchController.text);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Book Search")),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: "Search by title or author...",
                suffixIcon: IconButton(
                  icon: const Icon(Icons.search),
                  onPressed: _performSearch,
                ),
              ),
              onSubmitted: (_) => _performSearch(),
            ),
          ),
          Expanded(
            child: _searchResults == null
                ? const Center(child: Text("Search for a book to begin!"))
                : FutureBuilder<List<BookSearchResult>>(
                    future: _searchResults,
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const Center(child: CircularProgressIndicator());
                      } else if (snapshot.hasError) {
                        return const Center(
                          child: Text("Error fetching books."),
                        );
                      } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                        return const Center(child: Text("No books found."));
                      }
                      final books = snapshot.data!;

                      // List of books goes here
                      return ListView.builder(
                        itemCount: books.length,
                        itemBuilder: (context, index) {
                          final book = books[index];
                          return ListTile(
                            leading: Image.network(
                              book.smallThumbnail ?? "",
                              errorBuilder: (ctx, err, stackTrace) =>
                                  const Icon(Icons.book),
                            ),
                            title: Text(book.title),
                            subtitle: Text(book.authors.join(", ")),
                          );
                        },
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
