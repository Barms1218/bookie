import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user.dart';

class UserService {
  final String baseURL = "http://127.0.0.1";

  Future<User> register(UserRegister user) async {
    final url = Uri.parse("$baseURL/users/register?=$user");

    final response = await http.post(
      url,
      headers: <String, String>{
        "Content-Type": "application/json; charset=UTF-8",
      },
      body: jsonEncode(user.toJson()),
    );
    if (response.statusCode == 201) {
      final dynamic decodedData = jsonDecode(response.body);

      return decodedData.map((json) => User.fromJson(json));
    } else {
      throw Exception("User registration failed.");
    }
  }
}
