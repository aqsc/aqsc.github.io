---
layout: archive
title: 'CV'
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

# Education

- B.S. in Electronic Information Engineering, Shandong University, 2002.9 - 2006.6
- M.S. in Electronic Engineering, Zhejiang University, 2006.9 - 2008.7
- Ph.D in Information Engineering, Nanyang Technological University, 2008.8 - 2012.8

# Work experience

- 2019.3 - Present : Researcher

  - Fudan University

- 2017.8 - 2019.2 : Senior Machine Learning Researcher

  - Artificial Intelligence Institute Singapore - Huawei

- 2013.12 - 2017.7 : Researcher

  - Institute for Infocomm Research - Agency for Science, Technology and Research (A\*STAR)

- 2012.11 - 2013.4 : Researcher

  - The Advanced Remanufacturing and Technology Centre (ARTC) - Agency for Science, Technology and Research (A\*STAR)

- 2012.11 - 2013.4 : Associate Researcher

  - Intelligent Robot Lab – Nanyang Technological University

# Research Direction

- Machine Vision
- Image & Video Analytics
- Deep Learning
- Data Mining

# Honors and Awards

1. 2016, Ranked second in performance out of 30 fellows in the I2R Institute for Visual Computing, earning the I2R Top of Top Performer designation.
2. 2015, Ranked second in performance out of 30 fellows in the I2R Institute for Visual Computing, earning the I2R Top of Top Performer designation
3. 2014, Ranked first in performance out of 50 fellows in the I2R Institute for Visual Computing, earning the I2R Top of Top Performer designation
4. 2014, RIE2020 Research Planning Contribution Award (Robotics Direction), Singapore
5. 2008 to 2012, Recipient of Singapore Ministry of Education Research Scholarship
6. 2011, Student Travel Award Winner, IEEE International Conference on Image Processing
7. 2008, First Prize of Zhejiang University Challenge Cup Academic Competition
8. 2003 to 2005, Outstanding Student Scholarship of Shandong University
9. 2001, Third prize in the joint national high school mathematics competition
10. 1999, Second Prize of Shandong Junior High School Chemistry Olympiad

# Publications

<h2>Journal Articles</h2>
<ul>{% for post in site.publications reversed %}
  {% if post.pubtype == 'journal' %}
      {% include archive-single-cv.html %}
  {% endif %}
{% endfor %}</ul>

<h2>Conference Papers</h2>
<ul>{% for post in site.publications reversed %}
  {% if post.pubtype == 'conference' %}
      {% include archive-single-cv.html %}
  {% endif %}
{% endfor %}</ul>
  
<!-- Talks
======
  <ul>{% for post in site.talks %}
    {% include archive-single-talk-cv.html %}
  {% endfor %}</ul>
   -->
# Teaching
  <ul>{% for post in site.teaching %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
  
Service and leadership
======
* Director of the Embedded Deep Learning and Visual Analysis Lab
