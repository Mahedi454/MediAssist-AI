class User {
  final int id;
  final String email;
  final String fullName;
  final bool isActive;
  final bool isAdmin;
  final DateTime createdAt;

  const User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.isActive,
    required this.isAdmin,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      email: json['email'] as String,
      fullName: json['full_name'] as String? ?? '',
      isActive: json['is_active'] as bool? ?? true,
      isAdmin: json['is_admin'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
