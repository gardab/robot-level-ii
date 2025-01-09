from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    # Downloads the csv with orders details
    robot_orders = get_orders()
    open_robot_order_website()
    number_of_orders = robot_orders.size
    # Fill the form with order details for each robot in the csv and submits the form
    for order in robot_orders:
        # Closes the popup
        close_annoying_modal()
        current_order = order['Order number']
        # Fills and submits the form
        fill_the_form(order)
        receipt_pdf_path = store_receipt_as_pdf(current_order)
        robot_screenshot = screenshot_robot(current_order)
        embed_screenshot_to_receipt(robot_screenshot, receipt_pdf_path)
        # If there are still more orders, it clicks on the 'order another robot' button and continues
        if number_of_orders > int(current_order):
            order_another_robot()
    archive_receipts()
             
def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
def get_orders():
    """Downloads csv file with orders from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    robot_orders = library.read_table_from_csv(
        "orders.csv", header=True, columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    return robot_orders

def close_annoying_modal():
    """Clicks on the OK button on the annoying modal that pops up
    """
    page = browser.page()
    page.click("button:text('OK')")
    
def fill_the_form(order):
    """Fill the form to order a robot with the details from the csv and clicks on the preview button
    """
    page = browser.page()
    page.select_option("select#head", order['Head'])
    page.check(f"#id-body-{order['Body']}")
    page.fill("input[placeholder='Enter the part number for the legs']", order['Legs'])
    page.fill("#address", order['Address'])
    page.click("button:text('Preview')")
    page.click("button:text('order')")
    # If there is an error message retries submitting the form
    while page.is_visible("//*[@class='alert alert-danger']"):
        page.click("button:text('order')")
    
def order_another_robot():
    """Clicks on the 'Order another robot' button when the form has been successfully submitted
    """
    page = browser.page()
    while page.is_visible("//*[@class='alert alert-success']"):
        page.click("button:text('Order another robot')")
        
def store_receipt_as_pdf(order_number):
    """Takes the receipt information from the html page and stores it as a pdf file

    Args:
        order_number (int): Sequential number for the order. It is used as part of the pdf name

    Returns:
        str: The path to the pdf file
    """
    page = browser.page()
    robot_receipt_html = page.locator("#receipt").inner_html()
    order_number_zeros = order_number.zfill(3)
    pdf = PDF()
    receipt_pdf_path = f"output/receipts/receipt_{order_number_zeros}.pdf"
    pdf.html_to_pdf(robot_receipt_html, receipt_pdf_path)
    return receipt_pdf_path
        
def screenshot_robot(order_number):
    """Takes a screenshot of the ordered robot and stores it as a png image

    Args:
        order_number (int): Sequential number for the order. It is used as part of the pdf name

    Returns:
        str: The path to the png file
    """
    page = browser.page()
    order_number_zeros = order_number.zfill(3)
    robot_ss_path = f"output/receipts/robot_preview_{order_number_zeros}.png"
    page.screenshot(path=robot_ss_path)
    return robot_ss_path
    
def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Appends the screenshot of the robot to the pdf file with the receipt info

    Args:
        screenshot (str): Path to the robot screenshot
        pdf_file (str): Path to the pdf receipt file
    """
    pdf = PDF()
    list_of_files = [pdf_file, screenshot]
    pdf.add_files_to_pdf(files=list_of_files, target_document=pdf_file)
    
def archive_receipts():
    """Creates a zip file with all the pdf receipt files corresponding to the csv order.
    """
    receipts = Archive()
    receipts.archive_folder_with_zip('./output/receipts', './output/receipts.zip')