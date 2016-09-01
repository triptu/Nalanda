import requests, re, os, sys, getpass
from tqdm import tqdm
from bs4 import BeautifulSoup as bs

os.chdir(r'D:\DC++Share\2-1\new')

url='http://nalanda.bits-pilani.ac.in/login/index.php'
s= requests.session()
home_page = ''

all_courses = []
course_urls = []

def login():
    password = getpass.getpass()
    params ={'username':'f2015235', 'password':password}
    global home_page
    home_page = s.post(url, params)
    if home_page.status_code!=200:
        print "Something went wrong."
        sys.exit(0)
    elif 'Login to the site' in home_page.text[:200]:
        print "Invalid Login. Please try again."
        sys.exit(0)
    print "Login Successful."


def allCourses():
    soup = bs(home_page.text, 'html.parser')
    courses = soup.find_all('h2', class_='title')
    if len(courses)==0:
        print "No course found."
        sys.exit(0)

    for course in courses:
        full_name = course.text
        k = re.match(r'(?P<name>.*) \(.*\)',full_name)
        name = k.groupdict()['name']
        all_courses.append(name)
        course_urls.append(course.findChild()['href'])
    print "Course Details fetched."


def download(course, url):
    response = s.get(url, stream=True)
    name = url.split('/')[-1].replace('%20', ' ')
    name ='scasd'

    # For checking if its already downloaded.
    if os.path.exists(os.path.join(course, name)):
        return ' -Already downloaded.'

    # Make subjects folder if it not exists already
    if not(os.path.exists(course)):
        os.mkdir(course)

    # Downloading.
    print("")
    with open(os.path.join(course, name) , "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)
    return '---Successful.'



# slides is a list which has slide_name, url tuples in it
def slidesDown(course_name, slides):
    for slide, url in slides:
        # sometimes we can download just by clicking the slide
        if url.endswith('?forcedownload=1'):
            url = url.replace('?forcedownload=1','')
        if url[-3:] in ['pdf', 'ppt', 'zip', 'doc', 'txt', 'ptx', 'ocx']:
            print "Downloading -", slide,
            print download(course_name, url)
            continue

        elif 'folder' in url and 'mod_folder' not in url:
            folder(course_name, url)
            continue

        # Skipping those 'general Notice And Announcements' link and other such links
        if 'resource' not in url and 'pluginfile.php' not in url:
            continue

        # other times pdf is opened in the browser itself after clicking
        new = s.get(url)       # clicking the document(eg. pdf file)
        ns = bs(new.text, 'html.parser')
        doc = ns.find('object')    # pdf or ppt


        print "Downloading -", slide,
        print download(course_name, doc_link)




# For folders
def folder(course_name, url):
    newt = s.get(url)
    soup = bs(newt.text, 'html.parser')
    files = soup.find_all('span', class_="fp-filename-icon")
    slides = []
    for f in files:
        sname = f.text
        slides.append((sname, f.findChild()['href']))
    slidesDown(course_name, slides)


# Two options to call. Either give the position or send name and url
def scrape(pos):  # position of course in the global lists
    course_name = all_courses[pos]
    url = course_urls[pos]

    subject = s.get(url)   # page after clicking the course
    soup = bs(subject.text, 'html.parser')
    things = soup.find_all('div', attrs={'class':'activityinstance'})[1:]

    # checking if there is something.
    if len(things)==0:
        print("No slides found in ", course_name)

    slides = []   # Data format (name, url)
    for thing in things:
        sname = thing.text
        slides.append((sname[:sname.find('File')].strip(), thing.findChild()['href']))

    slidesDown(course_name, slides)

login()
allCourses()
url = 'http://nalanda.bits-pilani.ac.in/mod/resource/view.php?id=27987'
download('ascas', url)
#scrape(3)
#s.close()
'''
def main():
    login()
    allCourses()
    for i in range(len(all_courses)):
        retry = 0
        while retry<5:
            try:
                scrape(i)
                break
            except:
                retry+=1
        except:
            print "Problem with", all_courses[i]
    s.close()


if __name__ == '__main__':
    main()
 '''
