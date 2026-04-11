import 'package:flutter/material.dart';
import 'package:frontend/models/user.dart';
import 'package:frontend/services/user_service.dart';
import '../models/book.dart';
import 'package:frontend/services/book_service.dart';

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

  bool _isLoading = false; // To show a spinner while waiting

  // This is the "Future" function
  Future<void> _handleRegister() async {
    setState(() => _isLoading = true);

    try {
      final newUser = await _userService.register(
        UserRegister(
          name: _nameController.text,
          email: _emailController.text,
          password: _passwordController.text,
        ),
      );

      print("User registered: ${newUser.name}");
    } catch (e) {
      print("Error: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Bookie Login")),
      body: Stack(
        children: [
          Center(
            child: Column(
              children: [
                TextField(
                  controller: _nameController,
                  decoration: InputDecoration(hintText: "Username..."),
                ),
                TextField(
                  controller: _passwordController,
                  decoration: InputDecoration(hintText: "Password..."),
                ),
                TextField(
                  controller: _emailController,
                  decoration: InputDecoration(hintText: "Email..."),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
