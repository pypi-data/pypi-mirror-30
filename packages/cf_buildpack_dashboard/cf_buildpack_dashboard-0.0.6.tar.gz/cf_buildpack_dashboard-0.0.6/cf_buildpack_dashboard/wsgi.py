from cf_buildpack_dashboard.api.run import application

if __name__ == "__main__":
    port = environ.get("PORT", 5000)

    application.run("0.0.0.0", int(port))
