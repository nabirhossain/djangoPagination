# Properly Pagination in Django with bootstrap

## Django Pagination Display Issue: all the page numbers show up

  Problem 1. If number of pages becomes too many, the whole paginated view becomes unwieldy:

  Problem 2.The implementation does not handle query pagination properly. For example, if I search for 23rd page of all objects that contain the title = “Django”, the redirect should be to “someview.html?title=Django&page=23”, not “someview.html?page=23”.
>
### I solved this django pagination properly for many pages following this tutorial.

[Medium Tutorial](https://medium.com/@sumitlni/paginate-properly-please-93e7ca776432)

[Django snippet tutorial](https://djangosnippets.org/snippets/2199)

https://code.i-harness.com/en/q/571e9c
>--------------------------------------------
>[Django Deployment Guide](https://github.com/codingforentrepreneurs/Guides/blob/master/all/Heroku_Django_Deployment_Guide.md)

>[Django Virtual env setup](https://syscoding.com/tutorials/44/how-to-setup-python-virtualenv-on-ubuntu-1710/)
>
![Alt text](/path/to/img.jpg "Optional title")
