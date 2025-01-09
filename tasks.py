from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables

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
        # Fills and submits the form
        fill_the_form(order)
        # If there are still more orders, it clicks on the 'order another robot' button and continues
        if number_of_orders > int(order['Order number']):
            order_another_robot()
             
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
    page = browser.page()
    while page.is_visible("//*[@class='alert alert-success']"):
        page.click("button:text('Order another robot')")
        
        