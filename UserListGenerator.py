#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wikipedia, re, string

RE_USER = re.compile('\[\[[Uu]ser ?: ?(.*?) ?[\|\]]')
RE_LISTED = re.compile(' *[\*#] *(.+?)\W')
RE_RIBBONBEARER = re.compile('\{\{.*?name ?= ?(.*?) ?[\|\}]')

def identifyParticipants(text, page):
  sections = getSection(text, ("participant", "participants", "people", "participant?", "participants?", "people?"))
  linked = []
  if sections:
    linked = RE_USER.findall(sections)
    if not linked:
      #extract non user:-linked users from a list of participants
      linked = RE_LISTED.findall(sections)
  else:
    linked = RE_USER.findall(text)
  if not linked:
    #extract all named users from ribbons on the page
    linked = RE_RIBBONBEARER.findall(text)
  if not linked:
    history = page.getVersionHistory()
    #compare the edit history with the page content
    editors = [change[2] for change in history]
    for editor in editors:
      if editor.lower() in text.lower():
        linked.append(editor)
  map(string.strip, linked)
  return linked
  
def getUsers(page):
  """
returns a list of expeditions participants found in the text of a geohashing expedition page.
ingredients: one wikipedia.Page object
  """
  text = page.get()
  title = page.title()
  wikipedia.output(u'Parsing %s...' % title)

  if(text[0] == u"="):  # a hack?
    text = u"\n" + text

  if(text[1] == u"="):
     text = u"\n" + text

#Generate the list of people
#First look in appropriately named "who" sections
  peopleSecText = getSection(text, ("participant", "participants", "people", "participant?", "participants?", "people?"))
  if(peopleSecText != None):
    peopleText = getPeopleText(text, peopleSecText)

#If that fails, look for all unique [[User:*]] tags in the expedition page
  if((peopleSecText == None) or (len(peopleText) == 0)):
    peopleText = getUserList(text)

  return peopleText

def getSections(text):
   splitText = re.split("\n", text)
   minlen = 99
   for line in splitText:
       match = re.match("\s*=+", line)
       if ((match != None) and (len(string.strip(match.group(0))) < minlen)):
           minlen = len(string.strip(match.group(0)))

   equal_str = u""
   for i in range(0,minlen):
       equal_str += u"="
   match_str = u"\n\s*" + equal_str + "([^=]*?)" + equal_str

   text_arr = re.split(match_str, text)
   for i in range(0,len(text_arr)):
       text_arr[i] = string.strip(text_arr[i])

   section_hash = {}
   section_hash[""] = text_arr[0]

   for i in range(1,len(text_arr),2):
       section_hash[string.lower(text_arr[i])] = text_arr[i+1]

   return section_hash

def getSection(text, name_arr):
  """
This will look for a section with one of the names in name_arr
The search is case insensitive, and returns the first match, starting from name_arr[0] and continuing to name_arr[len(name_arr)-1]
It will return the body of the appropriate section, or None if there were no matches for the section name.
  """
  sections = getSections(text)
  for header in name_arr:
      if(header in sections):
          return sections[header]
  if ((len(name_arr) == 0) and ("" in sections)):
      return sections[""]
  return None

def getUserUist(text):
  """This will look for all unique user tags on a page, and make a list out of them."""
  regex_res = re.findall("\[\[User:.*?\]\]", text, re.I)
  regex_lower = []
  for i in range(0,len(regex_res)):
    regex_lower.append(re.sub("_", " ", regex_res[i].lower()))
    regex_lower[i] = re.sub(" ?| ?", "|", regex_lower[i])
    regex_lower[i] = re.sub("'s", "", regex_lower[i])
  result_arr = []
  for i in range(0,len(regex_lower)):
    for j in range(i+1,len(regex_lower)):
      if (regex_lower[i] == regex_lower[j]):
        break
      else:
        result_arr.append(regex_res[i])

  temp_str = u", "
  return temp_str.join(result_arr)

def getPeopleText(text, people_text):
  """This function will parse a list of users, and return them in a comma separated list."""
  people_text = re.sub("<!--.*?(-->|$)", "", people_text)
  people_text = string.strip(re.sub("^\[[^][]*?\]", "", people_text))
  people_text_arr = re.split("\n", people_text)

  people_text = u""

  if (len(people_text_arr[0]) == 0):
    people_regex_str = re.compile("^(\[\[.*?\]\]|[^ ]*)")
  elif (people_text_arr[0][0] == "*"):
    people_regex_str = re.compile("^\*\s*(\[\[.*?\]\]|[^ ]*)")
  elif (people_text_arr[0][0] == ":"):
    people_regex_str = re.compile("^:\s*(\[\[.*?\]\]|[^ ]*)")
  else:
    people_regex_str = re.compile("^(\[\[.*?\]\]|[^ ]*)")

  match_obj = people_regex_str.match(people_text_arr[0])
  people_text += match_obj.group(1)

  if(re.match("=", people_text_arr[0])):
    people_text = getUserList(text)
  else:
    for i in range(1,len(people_text_arr)):
      match_obj = people_regex_str.match(people_text_arr[i])
      if ((match_obj != None) and (len(match_obj.group(1)) != 0)):
        if(re.search("Category", people_text_arr[i])):
          pass
        elif (re.match("=", people_text_arr[i])):
          pass
        else:
          people_text += u", "
          people_text += match_obj.group(1)
  return people_text