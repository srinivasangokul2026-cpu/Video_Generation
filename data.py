import re
raw=open('script.txt',encoding='utf-8').read()
parts=re.split(r'\n?\s*स्लाइड (\d+) – ',raw.strip())
hi={}
for i in range(1,len(parts),2):
    t=parts[i+1].strip().split('\n',1)
    hi[int(parts[i])]=(t[0].strip(),t[1].strip())
en={
1:("Copyright Notice","This is a copyright, intellectual property and regulatory notice. All rights to this material are reserved by BOI Services Limited. Unauthorised use is strictly prohibited."),
2:("Welcome","Welcome to the BOI Services Limited platform. In this guide, we will learn how a CIBIL report is generated. This guide has been prepared by Gokul and Arjun."),
3:("Login Guide","A separate Login Guide is available for login-related information. To understand the login process, you can watch the Login Guide video."),
4:("Opening CIBIL Reports","First, click the Home icon on the left side of the dashboard. The side bar opens as soon as you click. Now, in the side bar, under Business, click CIBIL Reports."),
5:("Fetching a CIBIL Report","On the CIBIL Reports page, click the Fetch CIBIL Report button. A form opens as a pop-up. Fill in all the fields in this form correctly. After entering all the details, click the Fetch Report button to get the report."),
6:("CIBIL Report: The 7-Step Process","After you submit the details, the CIBIL report goes through seven stages. Stage one: Starting. Stage two: Waiting for OTP. Stage three: Verifying OTP. Stage four: Submitting application. Stage five: Waiting for report. Stage six: Downloading report. And stage seven: Completed. The whole process can take about one to two minutes. During any stage, do not refresh the page, do not go back, and do not close the browser tab."),
7:("Processing Status: Starting (Stage 1)","This is the first stage. The Status column shows starting, which means your request has begun. Let the process continue."),
8:("Processing Status: Waiting for OTP (Stage 2)","This is the second stage. The status shows waiting for OTP, which means the system is waiting for the OTP. This stage can take about one to two minutes. Please wait for the next stage."),
9:("Processing Status: Verifying OTP (Stage 3)","This is the third stage. The status shows verifying OTP, which means the OTP is being verified. Please wait without leaving the page."),
10:("Processing Status: Submitting Application (Stage 4)","This is the fourth stage. The status shows submitting application, which means the application is being submitted. Please keep the tab open."),
11:("Processing Status: Waiting for Report (Stage 5)","This is the fifth stage. The status shows waiting for report, which means the system is waiting to receive the CIBIL report. Please be patient."),
12:("Processing Status: Downloading Report (Stage 6)","This is the sixth stage. The status shows downloading report, which means the report is being downloaded. Please do not refresh the page or close the tab."),
13:("Processing Status: Completed (Stage 7)","This is the seventh and final stage. The status shows completed, which means the CIBIL report has been generated successfully."),
14:("Viewing or Downloading the CIBIL Report","When the status shows Completed, open the three-dot menu in the Actions column. Clicking these three dots shows the eye icon to view the report and the download icon to download it."),
15:("Viewing the CIBIL Report","To view the report on screen, click the eye icon in the Actions menu. The CIBIL report opens in a pop-up window. Here, you can see the Enhanced CreditVision score, Personal Loan score, and total EMI. After viewing the report, click the cross at the top right to close the pop-up."),
16:("Downloading the CIBIL Report","To download the report, click the download icon in the Actions menu. The report's HTML file is downloaded to your computer. The downloaded file appears at the top right of the browser with the word Done, indicating that the download is complete. Now click this HTML file. The report opens in the browser, where you can view the customer's details and the CIBIL TransUnion score in full."),
17:("Need Help","For help, contact your support team or drop an email to itsupport@boislindia.com."),
}
assert hi and sorted(hi)==list(range(1,len(hi)+1)), "Slide numbers in script.txt must start at 1 and be consecutive"