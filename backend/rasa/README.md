# Rasa Modular Data Directory

This directory contains all active Rasa YAML files for the Customer Care AI project. Files are organized by topic for clarity and maintainability.

## Structure

- `rules_greetings.yml`: Rules for greetings and conversation start
- `rules_fallback.yml`: Rules for fallback and misunderstood input
- `rules_forms.yml`: Rules for form activation and handling
- `nlu.yml`, `stories.yml`, `domain.yml`, etc.: Standard Rasa data files

## How to Contribute

- Add new rules, stories, or NLU examples in a new or existing topic file.
- Keep files focused and well-commented.
- Archive old or unused YAMLs in `archive/backups/`.

## YAML Imports

- All modular YAML files are imported via `data.yml`. This is the entry point for Rasa training and validation.

## How to Add New Data

- Add new NLU, stories, or rules in a new or existing topic file (e.g., `nlu_shipping.yml`, `stories_returns.yml`).
- Add the new file to the `import` list in `data.yml`.

## How to Validate and Train

- To validate all data:

  ```bash
  rasa data validate --data backend/rasa/data.yml
  ```

- To train a model using all modular data:

  ```bash
  rasa train --data backend/rasa/data.yml
  ```

---

For questions or issues, see the main project README or contact the maintainer.
