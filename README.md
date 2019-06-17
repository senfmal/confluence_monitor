# Confluence Monitor
This tiny little tool is meant to allow project managers, Scrum masters, product owners, line managers and such to keep track of what is going on on "their" Confluence space or regime.

Originally, it started as a monitor to see how frequently certain pages are updated, which is seen as an indicator how actively stakeholders and/or employees are informed about progress of projects and programmes.

For this, we encourage the person in charge for the communication to introduce heuristics for tagging content within Confluence. In general, there is one "main" tag, we call the theme of a particular undertaking within a Confluence space. Most likely, this will correspond with the name of a bigger project or a whole programme. This is the tag all pages should have in common in order to indicate their affiliation. However, since release 0.7, this affiliation is also assured if one of a page's ancestors is tagged with the theme tag.

Besides the theme tag, which is a mandatory piece of configuration (next to Confluence side and space), all additional tags are optional features and can be freely attached if desired. However, thresholds for updating periods, can be configured according to those tags and allow for differentiations like (this list is of course just a suggestion, and is not limited as such):
- News pages
- Project landing pages
- Status report pages
- Working package pages
- Meeting notes
- etc.
