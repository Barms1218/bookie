import 'package:flutter/material.dart';
import 'package:frontend/models/user.dart';
import 'package:frontend/services/user_service.dart';
import '../models/book.dart';
import 'package:frontend/services/book_service.dart';

class RegisterDTO {
  String name = '';
  String password = '';
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final UserService _userService = UserService();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final _registerDTO = RegisterDTO();

  bool _isLoading = false; // To show a spinner while waiting

  // This is the "Future" function
  Future<void> _handleRegister() async {
    setState(() => _isLoading = true);
    final _registerDTO = RegisterDTO();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          Center(
            child: Column(
              children: [
                AppBar(title: const Text("Bookie Login")),
                TextFormField(
                  decoration: InputDecoration(hintText: "Author Name (Email)"),
                  onSaved: (value) => _registerDTO.name = value ?? '',
                ),
                TextFormField(
                  controller: _passwordController,
                  decoration: InputDecoration(hintText: "Password..."),
                  onSaved: (value) => _registerDTO.password = value ?? '',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
