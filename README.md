# Учебный проект foodgram-project-react

### Описание
Приложение «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

### Немного о проекте
> Создано в соответствии с предоставленной документацией.
> Формат передачи данных JSON. Запросы к API начинаются с /api/
> Запросы к админке начинаются с /admin/
* Эндпоинт auth/: аутентификация.
* Эндпоинт users/: пользователи.
* Эндпоинт users/subscriptions/: список подписок.
* Эндпоинт users/<int:author_id>/subscribe/: подписаться на пользователя.
* Эндпоинт recipes/: спсиок рецептов.
* Эндпоинт recipes/<int:recipe_id>/shopping_cart/: добавить рецепт в список покупок.
* Эндпоинт recipes/download_shopping_cart/: скачать список покупок.
* Эндпоинт recipes/<int:recipe_id>/favorite/: добавить рецепт в избранные.
* Эндпоинт tags/: теги рецептов.
* Эндпоинт ingriients/: ингредиенты.

## Адрес сервера, на котором запущен проект
### http://158.160.17.163/

## Адрес админки
### http://158.160.17.163/admin/

Данные для входа в админку:
  email: admin@email.ru
  password: admin
  
Тестовый пользователь:
  email: Test_user_1@email.ru
  password: user-user


