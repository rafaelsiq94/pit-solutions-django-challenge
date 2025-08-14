import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GraphQLClient:
    """
    GraphQL client for fetching data from external APIs.
    Handles authentication, requests, and error handling.
    """

    def __init__(self, endpoint_url: str, headers: Optional[Dict[str, str]] = None):
        self.endpoint_url = endpoint_url
        self.headers = headers or {}
        self.session = requests.Session()

    def query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            Response data as dictionary

        Raises:
            requests.RequestException: If the request fails
            ValueError: If the response contains errors
        """
        payload = {"query": query, "variables": variables or {}}

        try:
            response = self.session.post(
                self.endpoint_url, json=payload, headers=self.headers, timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                error_messages = [
                    error.get("message", "Unknown error") for error in data["errors"]
                ]
                raise ValueError(f"GraphQL errors: {'; '.join(error_messages)}")

            return data.get("data", {})

        except requests.RequestException as e:
            logger.error(f"GraphQL request failed: {e}")
            raise
        except ValueError as e:
            logger.error(f"GraphQL response error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in GraphQL query: {e}")
            raise


class StarWarsGraphQLClient(GraphQLClient):
    """
    Specific GraphQL client for Star Wars API.
    Contains predefined queries and handles Star Wars specific data.
    """

    def __init__(self):
        # Star Wars GraphQL endpoint
        super().__init__(
            endpoint_url="https://graphql.org/graphql",
            headers={
                "Content-Type": "application/json",
            },
        )

    def get_planets_query(self) -> str:
        """
        Get the GraphQL query for fetching planets.

        Returns:
            GraphQL query string
        """

        return """
        query GetPlanets {
            allPlanets {
                planets {
                    id
                    name
                    population
                    climates
                    terrains
                }
            }
        }
        """

    def fetch_planets(self) -> Dict[str, Any]:
        """
        Fetch planets from the Star Wars API.

        Returns:
            Dictionary containing planets data and pagination info
        """
        query = self.get_planets_query()
        return self.query(query)
