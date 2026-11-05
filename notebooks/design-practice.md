# TV Show ERD

```mermaid
erDiagram
    SHOWS ||--o{ GENRES : has
    SHOWS ||--o{ STARS : "starred in by"
    PEOPLE ||--o{ STARS : "stars in"
    SHOWS ||--o{ WRITERS : "written by"
    PEOPLE ||--o{ WRITERS : writes
    SHOWS ||--o{ RATINGS : "rated by"

    SHOWS {
        int id PK
        string title
        int year
        int episodes
    }

    PEOPLE {
        int id PK
        string name
        int birth
    }

    GENRES {
        int show_id FK
        string genre
    }

    STARS {
        int show_id FK
        int person_id FK
    }

    WRITERS {
        int show_id FK
        int person_id FK
    }

    RATINGS {
        int show_id FK
        float rating
        int votes
    }
```
