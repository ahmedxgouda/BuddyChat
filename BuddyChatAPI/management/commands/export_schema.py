from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
import re

class Command(BaseCommand):
    help = "Export GraphQL schema and save it as README.md"

    def handle(self, *args, **kwargs):
        schema_file = "schema.graphql"
        output_file = "README.md"

        # Step 1: Export the GraphQL schema
        self.stdout.write("Exporting GraphQL schema...")
        call_command("graphql_schema", "--out", schema_file)
        self.stdout.write(f"Schema exported to {schema_file}")

        # Step 2: Generate minimal documentation for front-end developers
        self.stdout.write(f"Generating {output_file}...")
        try:
            with open(schema_file, "r", encoding="utf-8") as sf, open(output_file, "w", encoding="utf-8") as of:
                schema_content = sf.read()
                of.write("# 📊 BuddyChat API Documentation\n\n")
                of.write("## Overview\n\n")
                of.write("This file documents the GraphQL schema for BuddyChat API. The schema is divided into two sections: Queries, and Mutations.\n\n")

                # Extract queries, mutations, and app-specific types
                current_section = None
                count = 0
                for line in schema_content.splitlines():
                    if re.match(r'type Query', line):
                        current_section = "Queries"
                        of.write("## Queries\n\n")
                    elif re.match(r'type Mutation', line):
                        current_section = "Mutations"
                        of.write("## Mutations\n\n")
                    elif re.match(r'type (\w+)', line) and 'Query' not in line and 'Mutation' not in line:
                        app_type_match = re.match(r'type (\w+)', line)
                        if app_type_match:
                            app_type = app_type_match.group(1)
                            if count > 0:
                                of.write("```\n\n")
                            of.write(f"### {app_type}\n\n")
                            of.write(f"```graphql\n{line}\n\n")
                            current_section = None
                            count += 1
                    elif current_section and re.match(r'\s+\w+\(', line):
                        operation_match = re.match(r'\s+(\w+)\((.*)\): (\w+)', line)
                        if operation_match:
                            name, args, return_type = operation_match.groups()
                            if current_section in ["Queries", "Mutations"]:
                                of.write(f"- **{name}**({args}) → `{return_type}`\n")
                            else:
                                of.write(f"{line}\n")
                    else:
                        # if current_section:
                        of.write(f"{line}\n")
                    

            self.stdout.write(f"Successfully created {output_file}")
        except FileNotFoundError:
            self.stderr.write("Error: File not found during conversion.")
        except Exception as e:
            self.stderr.write(f"Error: Conversion process failed: {e}")

        # Clean up intermediate file
        if os.path.exists(schema_file):
            os.remove(schema_file)
            self.stdout.write(f"Removed temporary file {schema_file}")
