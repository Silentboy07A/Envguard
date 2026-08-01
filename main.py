from envguard import Env

env = Env("examples/sample.env")

print(env.str("DATABASE_URL"))
print(env.int("PORT"))
print(env.bool("DEBUG"))