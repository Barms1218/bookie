class BookSearchResult {
  final String id;
  final String title;
  final String? smallThumbnail;
  final List<String> authors;

  BookSearchResult({
    required this.id,
    required this.title,
    required this.smallThumbnail,
    required this.authors,
  });

  factory BookSearchResult.fromJson(Map<String, dynamic> json) {
    return BookSearchResult(
      id: json['id'],
      title: json['title'],
      smallThumbnail: json['small_thumbnail'],
      authors: ['authors'],
    );
  }
}

class BookCover {
  final String id;
  final String title;
  final String thumbnail;
  final List<String> authors;
  final String description;
  final List<String> categories;
  final int totalPages;

  BookCover({
    required this.id,
    required this.title,
    required this.thumbnail,
    required this.authors,
    required this.description,
    required this.categories,
    required this.totalPages,
  });

  factory BookCover.fromJson(Map<String, dynamic> json) {
    return BookCover(
      id: json['book_id'],
      title: json['title'],
      thumbnail: json['thumbnail'],
      authors: json['authors'],
      description: json['description'],
      categories: json['categories'],
      totalPages: json['totalPages'],
    );
  }
}

class UserBookCover {
  final String id;
  final String title;
  final String thumbnail;
  final List<String> authors;
  final String description;
  final BookTag tags;

  UserBookCover({
    required this.id,
    required this.title,
    required this.thumbnail,
    required this.authors,
    required this.description,
    required this.tags,
  });

  factory UserBookCover.fromJson(Map<String, dynamic> json) {
    return UserBookCover(
      id: json['book_id'],
      title: json['title'],
      thumbnail: json['thumbnail'],
      authors: json['authors'],
      description: json['description'],
      tags: json['tags'],
    );
  }
}

class BookTag {
  final String id;
  final String name;
  final int rating_value;

  BookTag({required this.id, required this.name, required this.rating_value});

  factory BookTag.fromJson(Map<String, dynamic> json) {
    return BookTag(
      id: json['id'],
      name: json['name'],
      rating_value: json['rating_value'],
    );
  }
}
