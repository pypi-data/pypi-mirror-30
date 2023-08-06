import csv
import errno
import heapq
import math
import os
import sqlite3
import time

from operator import itemgetter

###############################################################################

def create_dirs(file_path):
    """Create any directories needed for the specified file.
    
    If the directories already exists for the file, this will do nothing.
    """
    
    # Retrieve the directory for the file.
    directory = os.path.dirname(file_path)
    
    # Ensure the directory does not exist.
    if (not directory or os.path.isdir(directory)):
        return
        
    # Create the directory.
    try:
        os.makedirs(directory)
        
    # NOTE: It is possible that a race condition can allow the directory to be
    #       created in between checking if the directory exists and attempting 
    #       to make the directory. If this happens, an error will be thrown.
    except OSError as e:
        
        # If the error was not due to the directory already existing, something
        # else happened.
        if (e.errno != errno.EEXIST):
            raise
            
###############################################################################
            
def load_features(feature_file_path):
    """Load the array of features from the specified feature file.
    
    A feature file should be formatted as a .csv (Comma Separated Value)
    file with only one row. Essentially, this means that the file should
    be formatted as a text file with every value separated by a comma.
    """
    
    # Ensure the file exists.
    if (not os.path.isfile(feature_file_path)):
        raise ValueError('Could not find feature file %s' 
                         % feature_file_path)
                         
    # Read first row of values.
    with open(feature_file_path) as file:
        feature_reader = csv.reader(file)
        return next(feature_reader)
            
###############################################################################

def save_features(features, feature_file_path):
    """Save the array of features in a csv file at the specified path.
    The .csv file extension will not be automatically added to the file
    name.
    
    If the directory where the file is to be held does not already exist, it
    will be created.
    """
    
    # Ensure the file's directory exists.
    create_dirs(feature_file_path)
    
    # Save the list of features to the file.
    with open(feature_file_path, 'w') as file:
        csv.writer(file).writerow(features)
            
###############################################################################

def percent_difference(feature1, feature2):
    """Compares each values of two sets of features by percent difference.
    Returns the average of the percent difference
    """

    if len(feature1) != len(feature2):
        raise ValueError('Feature lengths are not of the same length')
    
    # Calculate the percent differences between each of the features.
    percent_differences = ((abs(f1 - f2), float(f1 + f2) / 2) #(Difference, Average) 
                           for f1, f2 in zip(feature1, feature2))
    
    percent_differences = [float(x[0]) / float(x[1]) if x[1] != 0 else 0 
                           for x in percent_differences]
                           
    # Calculate the average of the percent differences.
    return sum(percent_differences) / len(percent_differences)
    
###############################################################################

def euclidean_distance(point1, point2):
    """Calculates the euclidean distance between the 2 specified n-dimensional 
    points.
    """
    
    if len(point1) != len(point2):
        raise ValueError('The specified points do not have the same number of '
                         'dimensions')
        
    sum_of_squares = sum((x1 - x2) ** 2 for x1, x2 in zip(point1, point2))
    return math.sqrt(sum_of_squares)
    
###############################################################################

def search(feature_matrix, features, label=None, num_samples=1):
    """Search the specified feature matrix for sample whose features are most
    similar to the specified features.
    
    The feature matrix should contain each sample's identifier as the first
    element for each sample.
    
    If a label is specified, only the samples with the matching label will
    be searched. If the label is provided, it will be assumed that the last
    element of every row in the feature matrix is the label of sample. If the
    label is not provided, then it will be assumed that the feature matrix
    provides no labels.
    
    Returns the label followed by the percent difference of the most similar 
    sample.
    """
        
    # Filter out only the samples with the same label if the label was
    # provided.
    if (label):
        samples = [sample[:-1] for sample in feature_matrix 
                   if sample[-1] == label]

    else:
        samples = feature_matrix

    # Determine the distance between the features and each of the samples.
    differences = [(sample[0], euclidean_distance(features, sample[1:])) 
                   for sample in samples]
    
    # Find the samples with the smallest distances.
    return heapq.nsmallest(num_samples, differences, key=itemgetter(1))

###############################################################################

class SampleDao(object):
    """A SampleDao (Sample Database Access Object) provides access to a
    database that holds a variety of samples. The type of sample available
    depends on the type of sample passed into the constructor.
    
    SampleDao is abstract and should not be instantiated directly. Instead,
    a subclass should be made to adapt it to the appropriate sample type.
    """
    
    # The directory where all of the features are stored.
    _features_directory = r'Features/'
    
    def __init__(self, sample_type, database_file_name, table_name=None,
                 identifier_column_name='ID', label_column_name='Label'):
        """Initialize a new SampleDao for the specified sample type that
        accesses the database at the specified path. If the database does not
        already exist, it is created.
        
        Optional parameters:
            
            table_name - the name of the table in the database
            identifier_column_name - the name of the primary key colmumn
            label_column_name - the name of the column containing labels
            
        """
        
        # Set the sample type.
        self._sample_type = sample_type
        
        # Set the column names.
        self._identifier_column_name = identifier_column_name
        self._label_column_name      = label_column_name
        
        # Set the table name.
        self._table_name = table_name or '{0}s'.format(sample_type.__name__)
        
        # Ensure the directory for the database exists.
        create_dirs(database_file_name)
        
        # Set the features directory inside the same directory as the database.
        database_directory = os.path.dirname(database_file_name)
        self._features_directory = os.path.join(database_directory, 
                                                SampleDao._features_directory)
        
        # Create the connection for the database.
        #
        # Note: If the database file doesn't exist yet, this will create it.
        self._connection = sqlite3.connect(database_file_name)
        
        # If the samples table already exists in the database, alter it to add
        # any missing columns. If it doesn't already exist, create it.
        if (self.__table_exists()):
            self.__alter_table()
            
        else:
            self.__create_table()
        
    def __exit__(self):
        """Close the connection to the databse.
        
        This method provides compatibility with the "with" keyword.
        """
        self.close()
        
        
    def __alter_table(self):
        """Alter the table to add any missing columns. This should only be 
        called in the constructor if the table already exists.
        """
        
        # Find out what columns the table already contains.
        query = 'PRAGMA table_info({0})'.format(self.table_name)
        cursor = self._connection.cursor()
        cursor.execute(query)
        
        # Note: The resultset contains a record for each column. The name of
        #       the column is the second item.
        columns = set(column_record[1] for column_record in cursor)

        # Determine what columns are missing.
        required = set(feature[0] for feature 
                       in self.sample_type.feature_methods())
        required |= set((self.identifier_column_name, self.label_column_name))
        
        missing = required - columns
        
        # Alter the table to add the missing columns.
        if (not missing):
            return
        
        query = 'ALTER TABLE {0} '.format(self.table_name)
        for column in missing:
            self._connection.execute(query + 'ADD [{0}] TEXT'.format(column))
        
    def __create_table(self):
        """Construct the table to hold all of the samples. This should only
        be called in the constructor if the table does not already exist.
        """
        
        feature_names = [feature[0] for feature 
                                    in self.sample_type.feature_methods()]
        feature_query = ','.join('[%s] TEXT' % feature for feature 
                                                       in feature_names)
        
        query  = 'CREATE TABLE IF NOT EXISTS %s (' % self.table_name
        query += '%s TEXT PRIMARY KEY,' % self.identifier_column_name
        query += '%s TEXT' % self.label_column_name
        if (feature_query):
            query += ',{0}'.format(feature_query)
        query += ')'
                
        self._connection.execute(query)
                
    def __table_exists(self):
        """Determine if the table to hold all of the samples exists in the
        database already.
        """
        
        # Retrieve the number of tables with the table name from the database.
        cursor = self._connection.cursor()
        query = ("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                 "AND name=?")

        cursor.execute(query, (self.table_name,))
        
        return cursor.fetchone()[0] > 0
        
    @property
    def identifier_column_name(self):
        """Get the name of the column used for the primary key column in the
        database.
        """
        return self._identifier_column_name
    
    @property
    def label_column_name(self):
        """Get the name of the column used for the label in the database."""
        return self._label_column_name
        
    @property
    def sample_type(self):
        """Get the sample class type of the samples stored in the database
        accessed by this 
        """
        return self._sample_type
    
    @property
    def table_name(self):
        """Get the name of the table created in the database to hold the
        samples.
        
        By default, this returns the name of the sample type with an 's'
        appended to the end.
        """
        return self._table_name
        
    def add_sample(self, sample, verbose_callback=None):
        """Add the specified sample to the database.
        
        A function that takes a single string as an argument can be specified
        as the verbose_callback in order to print updates during the feature
        extraction process.
        """
        
        # Ensure the sample is of the correct type.
        if (not isinstance(sample, self.sample_type)):
            raise TypeError("Sample is of the incorrect type")
            
        # Retrieve the id, label, and set of features.
        id = sample.identifier
        label = sample.label
        
        features, feature_names = self.extract_features(sample, 
                                             verbose_callback=verbose_callback)
                
        # Construct the query to insert the record in the database.
        feature_names = ','.join('[%s]' % name for name in feature_names)
        feature_params = ','.join('?' * len(features))
        query = 'INSERT OR REPLACE INTO {0} ([{1}], [{2}], {3}) VALUES(?, ?, {4})'
        query = query.format(self.table_name, self.identifier_column_name,
                             self.label_column_name, feature_names,
                             feature_params)
          
        self._connection.execute(query, [id, label] + features)
        self._connection.commit()
        
    def close(self):
        """Closes the connection to the database."""
        self._connection.close()
        
    def exists(self, identifier):
        """Checks if a sample has the specified identifier in the database."""
        
        query = 'SELECT {0} FROM {1} WHERE {0} = ?'.format(
                                                   self.identifier_column_name,
                                                   self.table_name) 
        cursor = self._connection.cursor()
        cursor.execute(query, [identifier])
                
        return len(cursor.fetchall()) > 0

    def extract_features(self, sample, feature_methods=None, 
                         verbose_callback=None):
        """Extract the specified features from the specified sample.
        
        feature_methods should contain the features to extract, with each
        feature being represented as a list with the first element being the
        name of the feature and the second element being the unbounded feature
        method.
        
        verbose_callback is an optional callback function that takes a single
        string parameter. If supplied, it will be called periodically to
        update the progress of the extraction.
        
        The return value will be a tuple containing two parallel lists. The
        first list will be the list of the features extracted from the sample.
        If the feature was a single numerical value, that number will be the
        value. If the feature was a list of values, the list will be saved to
        a .csv value and the value will be the path to the saved file. The
        second list will contain the name of the feature corresponding to
        each element in the first list.
        """
        
        # Use the full list of feature methods by default.
        feature_methods = feature_methods or self.sample_type.feature_methods()
        
        features = []
        feature_names = []
        for feature_name, feature_method in feature_methods:
            
            # Log start
            if (verbose_callback):
                verbose_callback('Parsing {0} ... '.format(feature_name))
                start = time.clock()
            
            # Execute the method for the sample and retrieve the feature
            # value.
            value = feature_method(sample)
            
            # If the value is a list of features instead of a single value,
            # save the list to a csv file and insert the path to the file
            # in the database in place of a value.
            if (isinstance(value, (list, tuple))):
                
                # The file directory should have be:
                #
                #     {Features Directory}/{Table Name}/{Feature Name}/{Sample}
                #
                file_name = '%s.csv' % sample.identifier
                
                file_path = os.path.join(self._features_directory, 
                                         self.table_name, feature_name, 
                                         file_name)
                
                # Save the features to the file and then set the file path as 
                # the value to be written.
                save_features(value, file_path)
                value = file_path
            
            # Add the feature
            features.append(value)
            feature_names.append(feature_name)
            
            # Log end
            if (verbose_callback):
                elapsed = time.clock() - start
                verbose_callback('Finished in {0:.5} seconds\n'.format(elapsed))
                
        return (features, feature_names)
        
    def feature_matrix(self, include_ids=False, include_labels=False):
        """Retrieve a matrix containing all of the features (columns) for all
        of the samples (rows) in the database.
        
        The feature matrix is an m x n 2D array where m is the number of
        samples in the database and n is the number of columns in the database.
        
        Setting include_ids to true will include the ids column at the
        beginning.
        
        Setting include_labels to true will include the labels column at the
        end.
        """
        
        # Construct a query to grab all of the feature columns (and optionally
        # the label column) from the database.
        feature_methods = self.sample_type.feature_methods()
        columns = [method[0] for method in feature_methods]

        if (include_ids):
            columns.insert(0, self.identifier_column_name)

        if (include_labels):
            columns += self.label_column_name
        
        columns_string = ','.join('[%s]' % column for column in columns)
        query = 'SELECT {0} FROM {1}'.format(columns_string, self.table_name)
        
        cursor = self._connection.cursor()
        cursor.execute(query)
        
        # If a feature column holds multiple features, the value will be a 
        # string containing the path to a csv file that holds the list of
        # values. Otherwise, it will simply be a numerical value.
        feature_matrix = []
        for record in cursor:
            
            # Construct a list of all of the features in the cursor.
            features = []
            feature_matrix.append(features)
            
            # Handle IDs/Labels
            columns = record
            if (include_ids):
                features.append(columns[0])
                columns = columns[1:]
                
            if (include_labels):
                columns = columns[:-1]
            
            for value in columns:
                
                # Try to parse the value as a number.
                try:
                    features.append(float(value))
                    
                # If the value is not a number, it must be a path to a csv
                # file or empty (None).
                except:
                    if (value is None):
                        features.append(value)
                        
                    else:
                        features.extend(load_features(value))
                        
            # Add Label to end.
            if (include_labels):
                features.append(record[len(record)-1])
                    
        return feature_matrix
    
    def identifiers(self):
        """Retrieve a list of all of the identifiers for all of the samples in
        the database. All identifiers are guaranteed to uniquely identify a
        sample in the database.
        """
        
        # Construct query to grab identifier from table       
        query = 'SELECT {0} FROM {1}'.format(self.identifier_column_name,
                                             self.table_name)
        
        cursor = self._connection.cursor()
        cursor.execute(query)
        
        # The cursor is constructed as a list of records, with each record
        # holding a list of columns. In this case, there is only one column
        # in each record. Therefore, the cursor can simply be flattened into 
        # a regular list.
        return [str(label) for record in cursor for label in record]

    def labels(self):
        """Retrieve a dictionary of all of the labels associated with each
        sample. The keys for the dictionary will be the identifiers for each
        of the samples.
        """
        
        # Construct a query to grab the identifier and label from the table.        
        query = 'SELECT {0}, {1} FROM {2}'.format(self.identifier_column_name,
                                                  self.label_column_name,
                                                  self.table_name)
        
        cursor = self._connection.cursor()
        cursor.execute(query)
        
        # The ID is in the first column and the label is in the second column.
        # Use the ID as the key and the label as the value.
        return {str(record[0]): int(record[1]) if record[1] else None 
                                               for record in cursor}
                                               
    def missing_features(self, id):
        """Determine which feature columns the sample with the specified id
        is missing in the database.
        
        The missing columns will be returned as an list of strings 
        representing the column names.
        """
        
        # Retrieve all of the features for the specified sample.
        features = [feature[0] for feature 
                    in self.sample_type.feature_methods()]
        query = 'SELECT {0} FROM {1} WHERE {2} = ?'
        query = query.format(','.join('[%s]' % f for f in features),
                             self.table_name,
                             self.identifier_column_name)
        
        cursor = self._connection.execute(query, (id,))
        values = cursor.fetchone()
        
        # Find the features that have no value.
        return [feature for feature, value in zip(features, values) 
                if value is None]
                                             
    def samples(self, include_labels=False):
        """Retrieve all of the samples from the dictionary.
        
        The samples will be returned as a dictionary with the each sample's
        identifier representing the key for the sample. Each sample is
        represented by the array of its features.
        
        If include_labels is set to true, each feature's label will be appended
        to the array of features.
        """
        feature_matrix = self.feature_matrix(include_ids=True, 
                                             include_labels=include_labels)
        return {row[0]: row[1:] for row in feature_matrix}
        
    def save_feature_matrix(self, file_path, include_ids=False, 
                            include_labels=False):
        """Retrieve the feature matrix and save it to the specified file.
        
        file_path is the path to the file where the feature matrix should be
        saved.
        
        Setting include_ids to true will include the ids column at the
        beginning of the feature matrix.
        
        Setting include_labels to true will include the labels column at the
        end of the feature matrix.
        """
        
        # Retrieve feature matrix.
        feature_matrix = self.feature_matrix(include_ids=include_ids, 
                                             include_labels=include_labels)
                                             
        # Ensure the directory for the file exists.
        create_dirs(file_path)
                                             
        # Save feature matrix to file.
        with open(file_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(feature_matrix)
            
    def search(self, features, label):
        """Search the feature matrix for the sample whose features are most 
        similar to the specified features.
        
        Returns the label followed by the percent difference of the most 
        similar sample.
        """
        
        feature_matrix = self.feature_matrix(self, include_id=True, 
                                             include_labels=True)
        return search(feature_matrix, features, label)
        
    def update_sample(self, sample, features=None, verbose_callback=None):
        """Update the specified features for the specified sample in the
        database. If no features are specified, the sample will have only its
        missing features filled in.
        
        features should be a list of feature names. It should not contain the
        actual feature methods.
        
        verbose_callback is an optional callback function that takes a single
        string parameter. If supplied, it will be called periodically to
        update the progress of the extraction.
        """
        
        # Use the missing features by default.
        features = features or self.missing_features(sample.identifier)
        
        # Ensure there are features to update.
        if (not features):
            if (verbose_callback):
                verbose_callback('No features to update.\n')
                
            return
        
        # Retrieve the feature methods for each of the feature names.
        feature_methods = {feature[0]: feature[1] for feature 
                           in self.sample_type.feature_methods()}
        features = [(feature, feature_methods[feature]) 
                    for feature in features]
                    
        # Extract all of the features from the sample.
        features, feature_names = self.extract_features(sample, features, 
                                             verbose_callback=verbose_callback)
        
        # Update the sample in the database.
        query = 'UPDATE {0} SET '.format(self.table_name)
        query += ','.join('[%s]=?' % feature for feature in feature_names)
        query += ' WHERE [{0}]=?'.format(self.identifier_column_name)
        
        params = features + [sample.identifier]

        self._connection.execute(query, params)
        self._connection.commit()
