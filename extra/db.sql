CREATE TABLE authors (
    id serial PRIMARY KEY,
    value text NOT NULL
);

CREATE TABLE sources (
    id serial PRIMARY KEY,
    value text NOT NULL
);

CREATE TABLE quotes (
    id serial PRIMARY KEY,
    author_id integer REFERENCES authors (id) ON DELETE CASCADE,
    source_id integer REFERENCES sources (id) ON DELETE CASCADE,
    quote text NOT NULL
);

CREATE TABLE tags (
    id serial PRIMARY KEY,
    value text NOT NULL
);

CREATE TABLE quotes_tags (
    id serial PRIMARY KEY,
    quote_id integer REFERENCES quotes (id) ON DELETE CASCADE NOT NULL,
    tag_id integer REFERENCES tags (id) ON DELETE CASCADE NOT NULL,
    UNIQUE (quote_id, tag_id)
);
