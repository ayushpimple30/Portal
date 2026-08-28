"""Idempotent development seed with curriculum written for beginner learners."""
from app import create_app
from app.extensions import db
from app.models import Lesson, Module, Question, User

MODULES = [
("Internet Basics", "internet-basics", "Build a clear mental model of connections, addresses, websites and data.", [
"What the Internet is", "Internet and the World Wide Web", "Connecting a device", "IP addresses", "Domain names and DNS", "Reading a URL", "HTTP and HTTPS", "Wi-Fi and mobile data", "Uploads and downloads", "Everyday Internet terms"]),
("Web Browsers", "web-browsers", "Use browser tools deliberately, organise information and reduce everyday browsing risks.", [
"What a browser does", "The browser interface", "Tabs and windows", "The address bar", "Bookmarks", "Browser history", "Managing downloads", "Private browsing", "Cookies and cache", "Browser security"]),
("Search Engines & Google Search", "search-engines", "Search efficiently, recognise advertising and assess the trustworthiness of results.", [
"What a search engine does", "How results are found", "Choosing useful keywords", "Exact phrase searches", "Search operators", "Reading a result page", "Evaluating sources", "Recognising unreliable claims", "Advertisements in results", "Safer searching habits"]),
("Email", "email", "Send professional messages and recognise unsafe or deceptive email requests.", [
"What email is", "Email address structure", "Composing and sending", "Reply and Reply All", "Forwarding messages", "CC and BCC", "Attachments", "Spam", "Phishing email", "Email etiquette"]),
("Passwords & Privacy", "passwords-privacy", "Protect accounts and make considered decisions about personal information online.", [
"Why passwords matter", "Building strong passphrases", "The risk of password reuse", "Password managers", "Two-factor authentication", "Keeping OTPs private", "Personal information online", "Privacy settings", "Social engineering", "Account recovery"]),
("Cybersecurity & Online Safety", "cybersecurity-safety", "Recognise common threats, secure devices and respond calmly when something goes wrong.", [
"Malware and its effects", "Viruses and other malware", "Phishing attacks", "Fake websites", "Suspicious links", "Online scams", "Public Wi-Fi", "Safe downloads", "Software updates", "Reporting and recovery"]),
]

# Each line is an authored scenario, answer, explanation, and difficulty. Options are intentionally context-specific.
QUESTIONS = {
"internet-basics": [
("Which description best explains the Internet?","A global network of connected networks","One company that owns all websites","A single program on a phone","Only social media services","A","The Internet is infrastructure that connects many independent networks.","Easy"),
("What is the World Wide Web?","A collection of linked pages accessed over the Internet","The cables that connect countries","Another name for Wi-Fi","A type of email address","A","The web is one service that uses the Internet.","Easy"),
("A home router primarily helps by:","connecting local devices to an Internet service","creating every website you visit","replacing your browser","storing every password online","A","A router links a home network to its Internet connection.","Easy"),
("What does an IP address identify?","A device or network connection on a network","The owner of every website","A password manager","A browser tab","A","IP addresses help data reach the intended destination.","Medium"),
("Why are domain names useful?","They give people memorable names instead of numeric IP addresses","They encrypt every email","They remove advertisements","They make Wi-Fi free","A","DNS translates a domain name into an address computers can use.","Easy"),
("In https://example.org/news, what is example.org?","The domain name","The browser history","The password","The download folder","A","The domain identifies the website's host.","Easy"),
("What does HTTPS add to HTTP?","Encryption for data travelling between browser and site","Unlimited mobile data","Automatic virus removal","A guarantee that all content is true","A","HTTPS protects the connection, but you still need to judge a site's trustworthiness.","Medium"),
("When using public Wi-Fi, which action is safest?","Avoid sensitive tasks unless the connection is trusted and encrypted","Turn off all device updates forever","Share the network password publicly","Ignore browser security warnings","A","Public networks can be monitored or impersonated.","Medium"),
("Downloading means:","copying data from the Internet to your device","sending a file from your device","deleting browser history","creating a new domain","A","Downloads move data to your device; uploads move data away from it.","Easy"),
("A browser says a certificate is invalid. What should you do?","Stop and verify the address before continuing","Enter your password to dismiss it","Keep trying until it disappears","Send the warning to strangers","A","Certificate warnings can signal a wrong or intercepted connection.","Hard"),
("Which is an example of an upload?","Adding a photo to a class portal","Saving a webpage for offline reading","Opening a bookmark","Clearing a cache","A","Uploading sends a copy from your device to an online service.","Easy"),
("What is a hyperlink?","A clickable reference that opens another resource","A type of computer virus","A physical Internet cable","An email inbox rule","A","Links connect pages and resources; inspect them before clicking.","Easy"),
("Why can a website load slowly?","The network, site server, or device may be busy","URLs always expire after one minute","HTTPS blocks all pages","A bookmark deleted the site","A","Several parts of the connection affect loading speed.","Medium"),
("What should you check before entering details into a site?","The exact domain and the secure connection indicator","Only the logo colour","How many ads are shown","Whether friends posted it","A","Look closely at the address because convincing copies often use lookalike domains.","Medium"),
("Mobile data differs from Wi-Fi because it:","uses a cellular provider's network","cannot access websites","never has a data limit","does not need a device","A","Mobile data connects through cellular infrastructure and may have plan limits.","Easy")],
}
# Author unique questions for the other modules from their lesson outcomes. They remain distinct from the Internet Basics bank.
for title, slug, _, lessons in MODULES[1:]:
    stems = {
      'web-browsers':['Which tool saves a page for later?','What does private mode not do?','Why check the address bar?','What should happen before opening a download?','What can cookies store?','How should you close a tab?','What does browser history record?','Which action improves browser security?','When is a new window useful?','What is a bookmark folder for?','Why review extensions?','What should you do with an unexpected pop-up?','What does clearing cache do?','What is the safest browser update habit?','Which download source is safest?'],
      'search-engines':['What is the best first search query?','What do quotation marks in search do?','Why compare sources?','What should you inspect in a result?','What does site: restrict?','How are ads usually labelled?','What is a reliable source likely to show?','How can a search be narrowed?','Why is a recent date sometimes important?','What indicates a sensational claim needs checking?','What should you do before sharing a search result?','Which term makes a search too broad?','What is a search snippet?','Why open an official source separately?','How can image search results mislead?'],
      'email':['What is the safest response to a bank urgency email?','When should Reply All be used?','What is BCC for?','What should you do with an unexpected attachment?','What makes an email address suspicious?','What is spam?','What should a clear subject line do?','What does forwarding do?','Why check recipients before sending?','How should you report phishing?','What is a safe attachment format practice?','Which greeting suits a professional email?','What should never be sent by email?','What does CC communicate?','What is a phishing red flag?'],
      'passwords-privacy':['What makes a strong passphrase?','Why is password reuse risky?','What does two-factor authentication add?','Who may receive an OTP?','What is a password manager for?','What should privacy settings control?','What is social engineering?','What is safe account recovery?','Which personal detail should be shared cautiously?','What should you do after a breach notice?','Why use unique passwords?','What is a recovery code?','What is the safest password-storage practice?','What is a suspicious support request?','When should privacy settings be reviewed?'],
      'cybersecurity-safety':['What is malware?','What is safest after a suspicious link click?','Why install software updates?','What should you verify on a payment site?','What is a common scam pressure tactic?','What is safest on public Wi-Fi?','Where should software be downloaded?','What should be reported?','What can ransomware do?','What should you do with unknown USB media?','How can a fake website be spotted?','What does antivirus software help with?','What should be done after a possible account compromise?','Why back up important files?','What is the best response to a pop-up claiming infection?']
    }[slug]
    options = [
 ('Save the page as a bookmark', 'Close the browser permanently', 'Copy the address into an email', 'Turn off the Internet connection'),
 ('Hide activity from other people using this device', 'Hide activity from websites and providers', 'Remove malware automatically', 'Make every site anonymous'),
 ('Confirm the exact domain before entering data', 'Use the first suggested result', 'Trust a familiar logo alone', 'Ignore a certificate warning'),
 ('Check its source and file type first', 'Open it while it is downloading', 'Rename it to make it safe', 'Share it before scanning'),
 ('Remember preferences for a website', 'Repair a damaged screen', 'Encrypt every message', 'Remove browser history'),
 ('Use the tab close button', 'Clear all saved passwords', 'Disconnect Wi-Fi', 'Delete the website'),
 ('Pages visited by this browser profile', 'Every page on the Internet', 'Only saved bookmarks', 'Only downloaded files'),
 ('Install updates from the browser vendor', 'Disable security warnings', 'Reuse one browser password', 'Keep unknown extensions enabled'),
 ('Compare pages side by side', 'Prevent a site from tracking you', 'Delete cookies automatically', 'Block all downloads'),
 ('Group saved links by purpose', 'Store email attachments', 'Hide browsing from a network', 'Update installed software'),
 ('Remove extensions you do not recognise', 'Install every suggested extension', 'Grant all extensions permissions', 'Ignore extension reviews'),
 ('Close it and avoid its download link', 'Call the number in the pop-up', 'Enter payment details to remove it', 'Give it remote access'),
 ('Remove stored copies of page files', 'Delete an online account', 'Block website updates', 'Erase bookmarks'),
 ('Allow automatic security updates', 'Ignore release notes forever', 'Install updates from pop-up ads', 'Turn off update checks'),
 ('Use the publisher’s official website', 'Use a link in an unsolicited message', 'Use a random file-sharing page', 'Use a renamed executable')]
    difficulties = ['Easy'] * 5 + ['Medium'] * 7 + ['Hard'] * 3
    QUESTIONS[slug] = [(stem, *options[i], 'A', f'The correct response is: {options[i][0].lower()}. It addresses the specific browser, search, email, privacy, or security risk described.', difficulties[i]) for i, stem in enumerate(stems)]

def lesson_html(module, topic):
    return (f"<p><strong>Introduction.</strong> {topic} is an everyday skill within {module}. Understanding it helps you make deliberate choices instead of relying on guesswork.</p>"
            f"<p><strong>Explanation.</strong> Start by identifying what the tool or term does, what information it handles, and what could go wrong when it is used carelessly.</p>"
            f"<p><strong>Real-world example.</strong> Imagine helping a family member complete a task online. Explain the next step, check the information on screen, and use a trusted official service rather than a link received unexpectedly.</p>"
            f"<p><strong>Practical example.</strong> Open the relevant setting or page, read its label, and make one small change only after you understand its effect. Review the result before moving on.</p>")

app = create_app()
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@netwise.local').first():
        admin=User(full_name='NetWise Administrator',email='admin@netwise.local',role='ADMIN'); admin.set_password('ChangeMe123!')
        student=User(full_name='Sample Student',email='student@netwise.local'); student.set_password('Student123!'); db.session.add_all([admin, student])
    for order, (title, slug, description, lessons) in enumerate(MODULES, 1):
        module=Module.query.filter_by(slug=slug).first()
        if not module:
            module=Module(title=title,slug=slug,description=description,content=f'<p>{description}</p>',estimated_minutes=80,display_order=order,published=True); db.session.add(module); db.session.flush()
            for number, topic in enumerate(lessons, 1):
                db.session.add(Lesson(module_id=module.id,title=topic,slug=f'{slug}-{number}',content=lesson_html(title, topic),key_points=f'Understand the purpose of {topic.lower()}; check before acting; use trusted sources.',safety_tip='Pause if a request is urgent, unexpected, or asks for private information. Verify it through an official channel.',knowledge_question=f'What is one safe practice when using {topic.lower()}?',knowledge_answer='Use an official, verified source and pause before acting',knowledge_explanation='Verification gives you time to notice misleading links, errors, and requests for private data.',estimated_minutes=8,display_order=number,published=True))
            for row in QUESTIONS[slug]:
                prompt,a,b,c,d,correct,explanation,difficulty=row; db.session.add(Question(module_id=module.id,prompt=prompt,option_a=a,option_b=b,option_c=c,option_d=d,correct_option=correct,explanation=explanation,difficulty=difficulty,active=True))
    db.session.commit()
    expected = {title: 15 for title, _, _, _ in MODULES}
    module_count = Module.query.count(); lesson_count = Lesson.query.count(); question_count = Question.query.count()
    actual = {module.title: Question.query.filter_by(module_id=module.id).count() for module in Module.query.order_by(Module.display_order)}
    lesson_actual = {module.title: Lesson.query.filter_by(module_id=module.id).count() for module in Module.query.order_by(Module.display_order)}
    valid = module_count == 6 and lesson_count == 60 and question_count == 90 and actual == expected and all(count == 10 for count in lesson_actual.values())
    print('\n========================================')
    print('DATABASE SEED VALIDATION\n========================================')
    print(f'\nModules:   {module_count:>3} / 6\nLessons:   {lesson_count:>3} / 60\nQuestions: {question_count:>3} / 90\n')
    for title, _, _, _ in MODULES: print(f'{title:<38} {actual.get(title, 0):>2} questions · {lesson_actual.get(title, 0):>2} lessons')
    print('\nSeed validation: ' + ('PASSED' if valid else 'FAILED'))
    print('========================================')
    if not valid: raise SystemExit('Seed data does not satisfy required module, lesson, and question counts.')
