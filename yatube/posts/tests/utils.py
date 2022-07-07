def post_body_test(self, bundle):
    for first, second in bundle:
        with self.subTest():
            self.assertEqual(first, second)


def view_bundle(self, first_obj,
                additional_context=None,
                additional_value=None):

    """Принимает данные setUp, первый объект контекста формы,
    и необязательную пару для проверки контекст-значение, и
    компанует кортежи для проверки."""

    return ((first_obj.text, self.post.text),
            (first_obj.author.username, self.user.username),
            (first_obj.group.title, self.group.title),
            (additional_context, additional_value))
