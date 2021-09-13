class Stats(object):
    """
    Object for building query params for a global email statistics request
    """
    def __init__(
            self, start_date=None):
        """Create a Stats object

        :param start_date: Date of when stats should begin in YYYY-MM-DD format, defaults to None
        :type start_date: string, optional
        """
        self._start_date = None
        self._end_date = None
        self._aggregated_by = None
        self._sort_by_metric = None
        self._sort_by_direction = None
        self._limit = None
        self._offset = None

        # Minimum required for stats
        if start_date:
            self.start_date = start_date

    def __str__(self):
        """Get a JSON representation of this object.

        :rtype: string
        """
        return str(self.get())

    def get(self):
        """
        Get a JSON-ready representation of Stats

        :returns: This GlobalStats, ready for use in a request body.
        :rtype: response stats dict
        """
        stats = {}
        if self.start_date is not None:
            stats["start_date"] = self.start_date
        if self.end_date is not None:
            stats["end_date"] = self.end_date
        if self.aggregated_by is not None:
            stats["aggregated_by"] = self.aggregated_by
        if self.sort_by_metric is not None:
            stats["sort_by_metric"] = self.sort_by_metric
        if self.sort_by_direction is not None:
            stats["sort_by_direction"] = self.sort_by_direction
        if self.limit is not None:
            stats["limit"] = self.limit
        if self.offset is not None:
            stats["offset"] = self.offset
        return stats

    @property
    def start_date(self):
        """Date of when stats should begin in YYYY-MM-DD format

        :rtype: string
        """        
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        """Date of when stats should begin in YYYY-MM-DD format

        :param value: Date representing when stats should begin
        :type value: string
        """
        self._start_date = value

    @property
    def end_date(self):
        """Date of when stats should end in YYYY-MM-DD format

        :rtype: string
        """  
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        """Date of when stats should end in YYYY-MM-DD format

        :param value: Date representing when stats should end
        :type value: string
        """
        self._end_date = value

    @property
    def aggregated_by(self):
        """Chosen period (e.g. 'day', 'week', 'month') for how stats get grouped

        :rtype: string
        """        
        return self._aggregated_by

    @aggregated_by.setter
    def aggregated_by(self, value):
        """Chosen period (e.g. 'day', 'week', 'month') for how stats get grouped

        :param value: Period for how keys will get formatted
        :type value: string
        """        
        self._aggregated_by = value

    @property
    def sort_by_metric(self):
        """Metric to sort stats by

        :rtype: string
        """        
        return self._sort_by_metric

    @sort_by_metric.setter
    def sort_by_metric(self, value):
        """Metric to sort stats by

        :param value: Chosen metric stats will by sorted by
        :type value: string
        """        
        self._sort_by_metric = value

    @property
    def sort_by_direction(self):
        """Direction data will be sorted, either 'asc' or 'desc'

        :rtype: string
        """        
        return self._sort_by_direction

    @sort_by_direction.setter
    def sort_by_direction(self, value):
        """Direction data will be sorted, either 'asc' or 'desc'

        :param value: Direction of data, either 'asc' or 'desc'
        :type value: string
        """        
        self._sort_by_direction = value

    @property
    def limit(self):
        """Max amount of results to be returned

        :rtype: int
        """        
        return self._limit

    @limit.setter
    def limit(self, value):
        """Max amount of results to be returned

        :param value: Max amount of results
        :type value: int
        """        
        self._limit = value

    @property
    def offset(self):
        """Number of places a starting point of a data set will move

        :rtype: int
        """        
        return self._offset

    @offset.setter
    def offset(self, value):
        """Number of places a starting point of a data set will move

        :param value: Number of positions to move from starting point
        :type value: int
        """        
        self._offset = value


class CategoryStats(Stats):
    """
    object for building query params for a category statistics request
    """
    def __init__(self, start_date=None, categories=None):
        """Create a CategoryStats object

        :param start_date: Date of when stats should begin in YYYY-MM-DD format, defaults to None
        :type start_date: string, optional
        :param categories: list of categories to get results of, defaults to None
        :type categories: list(string), optional
        """        
        self._categories = None
        super(CategoryStats, self).__init__()

        # Minimum required for category stats
        if start_date and categories:
            self.start_date = start_date
            for cat_name in categories:
                self.add_category(Category(cat_name))

    def get(self):
        """
        Get a JSON-ready representation of this CategoryStats.

        :return: response category stats dict
        """
        stats = {}
        if self.start_date is not None:
            stats["start_date"] = self.start_date
        if self.end_date is not None:
            stats["end_date"] = self.end_date
        if self.aggregated_by is not None:
            stats["aggregated_by"] = self.aggregated_by
        if self.sort_by_metric is not None:
            stats["sort_by_metric"] = self.sort_by_metric
        if self.sort_by_direction is not None:
            stats["sort_by_direction"] = self.sort_by_direction
        if self.limit is not None:
            stats["limit"] = self.limit
        if self.offset is not None:
            stats["offset"] = self.offset
        if self.categories is not None:
            stats['categories'] = [category.get() for category in
                                   self.categories]
        return stats

    @property
    def categories(self):
        """List of categories

        :rtype: list(Category)
        """        
        return self._categories

    def add_category(self, category):
        """Appends a category to this object's category list

        :param category: Category to append to CategoryStats
        :type category: Category
        """
        if self._categories is None:
            self._categories = []
        self._categories.append(category)


class SubuserStats(Stats):
    """
    object of building query params for a subuser statistics request
    """    
    def __init__(self, start_date=None, subusers=None):
        """Create a SubuserStats object

        :param start_date: Date of when stats should begin in YYYY-MM-DD format, defaults to None
        :type start_date: string, optional
        :param subusers: list of subusers to get results of, defaults to None
        :type subusers: list(string), optional
        """        
        self._subusers = None
        super(SubuserStats, self).__init__()

        # Minimum required for subusers stats
        if start_date and subusers:
            self.start_date = start_date
            for subuser_name in subusers:
                self.add_subuser(Subuser(subuser_name))

    def get(self):
        """
        Get a JSON-ready representation of this SubuserStats.

        :return: response subuser stats dict
        """
        stats = {}
        if self.start_date is not None:
            stats["start_date"] = self.start_date
        if self.end_date is not None:
            stats["end_date"] = self.end_date
        if self.aggregated_by is not None:
            stats["aggregated_by"] = self.aggregated_by
        if self.sort_by_metric is not None:
            stats["sort_by_metric"] = self.sort_by_metric
        if self.sort_by_direction is not None:
            stats["sort_by_direction"] = self.sort_by_direction
        if self.limit is not None:
            stats["limit"] = self.limit
        if self.offset is not None:
            stats["offset"] = self.offset
        if self.subusers is not None:
            stats['subusers'] = [subuser.get() for subuser in
                                 self.subusers]
        return stats

    @property
    def subusers(self):
        """List of subusers

        :rtype: list(Subuser)
        """
        return self._subusers

    def add_subuser(self, subuser):
        """Appends a subuser to this object's subuser list

        :param subuser: Subuser to append to SubuserStats
        :type subuser: Subuser
        """
        if self._subusers is None:
            self._subusers = []
        self._subusers.append(subuser)


class Category(object):
    """
    Represents a searchable statistics category to be used in a CategoryStats object
    """
    def __init__(self, name=None):
        """Create a Category object

        :param name: name of category, defaults to None
        :type name: string, optional
        """        
        self._name = None
        if name is not None:
            self._name = name

    @property
    def name(self):
        """Get name of category

        :rtype: string
        """
        return self._name

    @name.setter
    def name(self, value):
        """Set name of category

        :param value: name of the statistical category
        :type value: string
        """        
        self._name = value

    def get(self):
        """
        Get a string representation of Category.

        :return: string of the category's name
        """
        return self.name


class Subuser(object):
    """
    Represents a searchable subuser to be used in a SubuserStats object
    """    
    def __init__(self, name=None):
        """Create a Subuser object

        :param name: name of subuser, defaults to None
        :type name: string, optional
        """        
        self._name = None
        if name is not None:
            self._name = name

    @property
    def name(self):
        """Get name of the subuser

        :rtype: string
        """        
        return self._name

    @name.setter
    def name(self, value):
        """Set name of the subuser

        :param value: name of the subuser
        :type value: string
        """        
        self._name = value

    def get(self):
        """
        Get a string representation of Subuser.

        :return: string of the subuser's name
        """
        return self.name
