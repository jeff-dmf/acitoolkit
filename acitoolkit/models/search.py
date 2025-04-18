"""
Search functionality for the ACI Toolkit.
This module provides classes and functions for searching and querying the ACI fabric.
"""

from typing import Optional, List, Dict, Any, Type, Union
import logging
from ..core.base import BaseACIObject
from ..acisession import Session
from ..aciTable import Table

log = logging.getLogger(__name__)

class SearchQuery:
    """
    ACI Search Query class.
    
    This class represents a search query in the ACI fabric. It provides methods
    for building and executing search queries.
    
    Attributes:
        target_class (str): The target APIC class to search
        query_string (str): The query string
        filters (Dict[str, Any]): Dictionary of query filters
    """
    
    def __init__(self, target_class: str) -> None:
        """
        Initialize a new search query.
        
        Args:
            target_class: The target APIC class to search
        """
        self.target_class = target_class
        self.query_string = ''
        self.filters = {}
        log.info("Created new search query for class: %s", target_class)
    
    def add_filter(self, key: str, value: Any, operator: str = 'eq') -> None:
        """
        Add a filter to the search query.
        
        Args:
            key: The filter key
            value: The filter value
            operator: The filter operator ('eq', 'ne', 'gt', 'lt', 'ge', 'le')
        """
        self.filters[key] = {
            'value': value,
            'operator': operator
        }
        log.debug("Added filter: %s %s %s", key, operator, value)
    
    def set_query_string(self, query_string: str) -> None:
        """
        Set the query string for the search query.
        
        Args:
            query_string: The query string
        """
        self.query_string = query_string
        log.debug("Set query string: %s", query_string)
    
    def build_query(self) -> Dict[str, Any]:
        """
        Build the search query.
        
        Returns:
            Dictionary containing the search query
        """
        query = {
            'targetClass': self.target_class,
            'queryString': self.query_string,
            'filters': self.filters
        }
        log.debug("Built query: %s", query)
        return query

class SearchResult:
    """
    ACI Search Result class.
    
    This class represents the results of a search query in the ACI fabric.
    
    Attributes:
        query (SearchQuery): The search query
        results (List[Dict[str, Any]]): List of search results
        total_count (int): Total number of results
    """
    
    def __init__(self, query: SearchQuery) -> None:
        """
        Initialize a new search result.
        
        Args:
            query: The search query
        """
        self.query = query
        self.results = []
        self.total_count = 0
        log.info("Created new search result for query: %s", query.target_class)
    
    def add_result(self, result: Dict[str, Any]) -> None:
        """
        Add a result to the search results.
        
        Args:
            result: The search result
        """
        self.results.append(result)
        self.total_count += 1
        log.debug("Added result: %s", result)
    
    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get all search results.
        
        Returns:
            List of search results
        """
        return self.results
    
    def get_total_count(self) -> int:
        """
        Get the total number of results.
        
        Returns:
            The total number of results
        """
        return self.total_count
    
    def get_json(self) -> Dict[str, Any]:
        """
        Get the JSON representation of the search results.
        
        Returns:
            Dictionary containing the JSON representation of the search results
        """
        return {
            'query': self.query.build_query(),
            'results': self.results,
            'totalCount': self.total_count
        }

class SearchEngine:
    """
    ACI Search Engine class.
    
    This class provides methods for executing search queries in the ACI fabric.
    
    Attributes:
        session (Session): The APIC session
    """
    
    def __init__(self, session: Session) -> None:
        """
        Initialize a new search engine.
        
        Args:
            session: The APIC session
        """
        self.session = session
        log.info("Created new search engine")
    
    def execute_query(self, query: SearchQuery) -> SearchResult:
        """
        Execute a search query.
        
        Args:
            query: The search query
            
        Returns:
            The search results
        """
        result = SearchResult(query)
        query_data = query.build_query()
        
        try:
            response = self.session.query(query_data)
            if response.ok:
                data = response.json()
                for item in data.get('imdata', []):
                    result.add_result(item)
                log.info("Executed query successfully: %d results", result.total_count)
            else:
                log.error("Query failed: %s", response.text)
        except Exception as e:
            log.error("Error executing query: %s", str(e))
        
        return result
    
    def search_by_class(self, target_class: str, filters: Optional[Dict[str, Any]] = None) -> SearchResult:
        """
        Search by APIC class.
        
        Args:
            target_class: The target APIC class
            filters: Optional dictionary of filters
            
        Returns:
            The search results
        """
        query = SearchQuery(target_class)
        if filters:
            for key, value in filters.items():
                query.add_filter(key, value)
        return self.execute_query(query)
    
    def search_by_string(self, target_class: str, query_string: str) -> SearchResult:
        """
        Search by query string.
        
        Args:
            target_class: The target APIC class
            query_string: The query string
            
        Returns:
            The search results
        """
        query = SearchQuery(target_class)
        query.set_query_string(query_string)
        return self.execute_query(query) 