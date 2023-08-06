Changelog
=========


0.0.2 (2018-04-09)
------------------

New
~~~
- Major update. [Valentin Lab]

  - GitCommit: does not recognize magic identifier ``LAST`` anymore.
  - GitCommit: added new attributes to access direct info of commit
    ``sha1_short``, ``author_email``, ``parent_list_string``, ``decorate_string``
  - GitCommit: added pythonic access to generic trailer values using
    ``trailer_LABEL`` attributes. Supports multi-valued trailer values.
  - GitCommit: specific ``authors``, ``author_names`` special attributes
    that leverage ``Co-Authored-By`` trailer value and commit author to
    provide a full list of authors.
  - GitCommit: new ``parents`` attribute to get the GitCommit parent list.
  - GitCommit: new ``tags_name`` attribute to get the list of tags attributed
    to current commit, along with ``tags`` that iterates through new ``GitTag``
    objects of the current commit, and ``.tag(label)`` method to instantiate
    a ``GitTag`` of current commit thanks to its label.
  - GitCommit: support of ``<`` (less-than) operator to map as close as possible
    with order relation of commits given by command git log.
  - GitCommit: support of ``in`` (``.__contains__(..)``) operator to map with
    ancestor relationship.
  - new ``GitTag``object that represent annotated tags and non-annotated tags,
    check ``README.rst`` for usage.
  - GitRepos: new ``.create(..)`` classmethod to create a new git repository.
  - GitRepos: new ``.init(..)`` classmethod to create a new git repository from
    an existing repository.
  - GitRepos: new ``.Tag(label)`` method to get a GitTag object from a given label.
  - GitRepos: renamed ``.commit(..)`` method to ``.Commit(..)``. Old method still
    kept for compatibility reason.
  - GitRepos: renamed ``.config(..)`` method to ``.Config(..)``. Old method still
    kept for compatibility reason.
  - GitRepos: API CHANGE: ``.log(..)`` method is now closer to ``git log`` command
    line usage, and ``includes``, ``excludes``, ``include_merge`` arguments have
    been removed. Please refer to documentation for more information.

Fix
~~~
- Catches bad repository when using ``GitRepos.log()``. [Valentin Lab]
- ``GitConfig()`` would fail if no arg. [Valentin Lab]


0.0.1 (2015-02-05)
------------------
- First import. [Valentin Lab]


