import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/book.dart';

class BookService {
  final String baseURL = "http://127.0.0.1";

  Future<List<BookSearchResult>> searchBooks(String query) async {
    final url = Uri.parse("$baseURL/search?=$query");

    final response = await http.get(url);

    if (response.statusCode == 200) {
      final List<dynamic> decodedData = jsonDecode(response.body);

      return decodedData
          .map((json) => BookSearchResult.fromJson(json))
          .toList();
    } else {
      throw Exception("Failed to load books.");
    }
  }

  Future<bool> addToLibrary(String bookId) async {
    final url = Uri.parse("$baseURL/books/add");

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"book_id": bookId}),
    );

    return response.statusCode == 201 || response.statusCode == 200;
  }
}
