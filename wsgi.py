from app import create_app

server = create_app()

if __name__ == "__main__":
    server.run(host='0.0.0.0')


# from myproject import app as application
#
# if __name__ == "__main__":
#     application.run(host='0.0.0.0')
