CREATE TABLE "users" (
  "id" UUID PRIMARY KEY,
  "name" Text,
  "role" Text,
  "email" Text,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "places" (
  "id" UUID PRIMARY KEY,
  "name" Text,
  "description" Text,
  "user_id" UUID,
  "country" Text,
  "place" Text,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "recommended" (
  "id" UUID PRIMARY KEY,
  "name" Text,
  "description" Text,
  "place_id" UUID,
  "country" Text,
  "place" Text,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "favorites" (
  "id" UUID PRIMARY KEY,
  "user_id" UUID,
  "places_id" UUID,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

ALTER TABLE "places" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "recommended" ADD FOREIGN KEY ("place_id") REFERENCES "places" ("id");

ALTER TABLE "favorites" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "favorites" ADD FOREIGN KEY ("places_id") REFERENCES "places" ("id");