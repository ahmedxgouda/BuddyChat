from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
import json

class Command(BaseCommand):
    help = "Export GraphQL schema and save it as README.md"

    def handle(self, *args, **kwargs):
        schema_file = "schema.json"
        output_file = "README.md"

        # Step 1: Export the GraphQL schema as JSON
        self.stdout.write("Exporting GraphQL schema...")
        call_command("graphql_schema", "--out", schema_file)
        self.stdout.write(f"Schema exported to {schema_file}")

        # Step 2: Generate minimal documentation for front-end developers
        self.stdout.write(f"Generating {output_file}...")
        try:
            with open(schema_file, "r", encoding="utf-8") as sf, open(output_file, "w", encoding="utf-8") as of:
                schema_content = json.load(sf)
                of.write("# 📊 BuddyChat API Documentation\n\n")
                of.write("## Overview\n\n")
                of.write("This file documents the GraphQL schema for BuddyChat API. The schema is divided into two sections: Queries, and Mutations.\n\n")

                for type_data in schema_content["data"]["__schema"]["types"]:
                    type_name = type_data["name"]
                    if type_data["kind"] == "OBJECT":
                        if type_name == "Query":
                            of.write("## Queries\n\n")
                        elif type_name == "Mutation":
                            of.write("## Mutations\n\n")
                        else:
                            description = type_data.get("description", "No description available.")
                            of.write(f"### {type_name}\n\n")
                            of.write(f"**Description:** {description}\n\n")
                            of.write("```graphql\n")
                            of.write(f"type {type_name} {{\n")

                        for field in type_data.get("fields", []):
                            args = ", ".join(
                                [f"{arg['name']}: {arg['type']['name']}" for arg in field.get("args", [])]
                            )
                            return_type = field["type"].get("name") or field["type"].get("ofType", {}).get("name")
                            field_description = field.get("description", "No description available.")
                            of.write(f"- **{field['name']}**({args}) → `{return_type}`\n")
                            of.write(f"  *Description:* {field_description}\n\n")

                        if type_name not in ["Query", "Mutation"]:
                            of.write("}\n\n```\n\n")

            self.stdout.write(f"Successfully created {output_file}")
        except FileNotFoundError:
            self.stderr.write("Error: File not found during conversion.")
        except Exception as e:
            self.stderr.write(f"Error: Conversion process failed: {e}")

        # Clean up intermediate file
        if os.path.exists(schema_file):
            os.remove(schema_file)
            self.stdout.write(f"Removed temporary file {schema_file}")
