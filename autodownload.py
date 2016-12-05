import requests, re, os, sys, getpass
from tqdm import tqdm
from bs4 import BeautifulSoup as bs

os.chdir(r'D:\DC++Share\2-1\new')

url='http://nalanda.bits-pilani.ac.in/login/index.php'
s= requests.session()
home_page = ''

all_courses = []
course_urls = []
new_downloads = {}

def login():
    # username = raw_input('Username: ')
    username = 'f2015235'
    print 'Username:', username
    password = getpass.getpass()
    params ={'username':username, 'password':password}
    global home_page
    home_page = s.post(url, params)
    if home_page.status_code!=200:
        print "Something went wrong."
        sys.exit(0)
    elif 'Login to the site' in home_page.text[:200]:
        print "Invalid Login. Please try again."
        sys.exit(0)
    print "Login Successful."


# Gets the name and link of all subjects listed on homepage.
def getAllCourses():
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
    print "Course Details fetched.\n\n"


def download(course, url):
    response = s.get(url, stream=True)

    name = url.split('/')[-1].replace('%20', ' ')

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
    new_downloads[course]+=1
    return '---Successful.'


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


# slides is a list which has slide_name, url tuples in it
def slidesDown(course_name, slides):
    for slide, url in slides:
        if url.endswith('?forcedownload=1'):
            url = url.replace('?forcedownload=1','')

        '''Lots of cases.'''
        # sometimes we can download just by clicking the slide
        if url[-3:] in ['pdf', 'ppt', 'zip', 'doc', 'docx', 'txt', 'ptx', 'ocx', 'xls', 'xlsx']:
            print "Downloading -", slide,
            print download(course_name, url)
            continue

        # Sometimes the link is a folder.
        elif 'folder' in url and 'mod_folder' not in url:
            folder(course_name, url)
            continue

        # Skipping those 'general Notice And Announcements' link and other such links
        elif 'resource' not in url:
            continue

        # other times pdf is opened in the browser itself after clicking
        new = s.get(url)       # clicking the document(eg. pdf file)
        # Sometimes clicking the link downloads directly
        # even though the link doesn't directly point to file.
        if new.url[-3:] in ['pdf', 'ppt', 'zip', 'doc', 'docx', 'txt', 'ptx', 'ocx', 'xls', 'xlsx']:
            print "Downloading -", slide,
            print download(course_name, new.url)
            continue

        # And finally for the times when pdf is opened in portal itself.
        ns = bs(new.text, 'html.parser')
        doc = ns.find('object')                                          # eg pdf or ppt
        if doc is not None:                                              # If something is found
            doc_link = doc['data']
            print "Downloading -", slide,
            print download(course_name, doc_link)
            continue
        else:                                                            # For downloading the images
            img = ns.find('div', class_='resourceimg')
            if img is not None:
                img_link = img.findChild()['src']
                print "Downloading - ", slide,
                print download(course_name, img_link)
                continue

        print "Some weird unaccounted case occured for file url: ", url  # When nothing works.


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

    return slides


def main():
    login()
    getAllCourses()
    for i in range(len(all_courses)):
        course_name = all_courses[i]
        # DEBUG start                                        "DEBUGGING"
        if "ELCTRONIC" not in course_name:
            continue
        #END
        new_downloads[all_courses[i]] = 0
        print "---------------%s------------"  %(all_courses[i])
        retry = 0
        while retry<5:
            # TODO:- Add separate case for when problem is in downloading and not scraping. So that
            # it doesn't repeatedly start from the beginning.
            try:
                slides = scrape(i)
                slidesDown(course_name, slides)
                if new_downloads[course_name] == 0:
                    print "Nothing new to download."
                else:
                    print "Total files downloaded -",new_downloads[all_courses[i]]
                break
            except Exception as e:
                print "Error ", str(e)                      # For "DEBUGGING"
                retry+=1
        else:
            print "Problem with", all_courses[i]
        print "-----------------------------------------------------------\n\n"
    s.close()


if __name__ == '__main__':
    main()

# Test file:-
#http://nalanda.bits-pilani.ac.in/pluginfile.php/82943/mod_resource/content/1/lecture%201.pdf

