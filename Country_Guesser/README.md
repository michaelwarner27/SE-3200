# Resourceful - Country Data Manager

## Resource

The resource for this project is **countries of the world**. 

### Attributes

- **Common Name** - The commonly used name for the country
- **Official Name** - The official, formal name of the country
- **Population** - The population count
- **HTML Flag Code** - HTML entity code for displaying the country's flag
- **Area in sqMI** - The total area of the country in square miles

## Database

### Schema 

```sql
CREATE TABLE countries(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  common_name TEXT NOT NULL,
  official_name TEXT NOT NULL,
  population INTEGER NOT NULL,
  html_flag_code TEXT NOT NULL,
  area INTEGER NOT NULL
)
```

### Database Class

All database methods return data as dictionaries with column names as keys for easy JSON serialization.