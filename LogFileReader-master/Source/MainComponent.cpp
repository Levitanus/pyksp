

#include "MainComponent.h"


//==============================================================================
MainContentComponent::MainContentComponent() : fontSize(16), filename("C:/logger.nka"), programWidth(800), programHeight(700)
{
	readSettingsFile();


	addAndMakeVisible(&textBox);
	textBox.setMultiLine(true);
	textBox.setReadOnly(true);
	textBox.setScrollbarsShown(true);
	textBox.setColour(TextEditor::backgroundColourId, Colour(0xff1a1a1a));
	textBox.setColour(TextEditor::textColourId, Colours::white);
	textBox.setColour(TextEditor::highlightColourId, Colour(0xff929292));
	//textBox.setScrollToShowCursor(false);

	setFontSize(fontSize);


	addAndMakeVisible(&pause);
	pause.setText("Freeze");
	pause.setClickingTogglesState(true);

	addAndMakeVisible(&autoScroll);
	autoScroll.setText("Auto Scroll");
	autoScroll.setClickingTogglesState(true);
	autoScroll.addListener(this);

	addAndMakeVisible(&zoomIn);
	zoomIn.setText("Zoom In");
	zoomIn.addListener(this);
	zoomIn.setRepeatSpeed(200, 40);
	
	addAndMakeVisible(&zoomOut);
	zoomOut.setText("Zoom Out");
	zoomOut.addListener(this);
	zoomOut.setRepeatSpeed(200, 40);

	addAndMakeVisible(&fileChooser);
	fileChooser.setText("Select File");
	fileChooser.addListener(this);
	
	addAndMakeVisible(&filenameLabel);
	setFilenameLabel();

    setSize (programWidth, programHeight);
	startTimer(150);
}

MainContentComponent::~MainContentComponent()
{
	writeSettingsFile();
}

void MainContentComponent::paint (Graphics& g)
{
	//if (this->getPeer() != nullptr && initFlag == true) {
	//	initFlag = false;
	//	this->getPeer()->setBounds(boundsFromSettingsFile, setFullscreenFlag);
	//}
	g.fillAll (( Colour (0xff4f4f4f)));

}

void MainContentComponent::resized()
{
	textBox.setBounds(0, 30, getWidth(), getHeight() - 30);

	static const int gap = 1;
	static const int height = 30;
	static const int width = 100;
	pause.setBounds(0, 0, width, height);
	autoScroll.setBounds(pause.getRight() + gap, 0, width, height);
	zoomIn.setBounds(autoScroll.getRight() + gap, 0, width, height);
	zoomOut.setBounds(zoomIn.getRight() + gap, 0, width, height);
	fileChooser.setBounds(zoomOut.getRight() + gap, 0, width, height);
	filenameLabel.setBounds(fileChooser.getRight() + 15, 0, 400, height);


	//if (this->getPeer() != nullptr)
	//{
	//	if (this->getPeer()->isFullScreen() == false)
	//	{
	//		programWidth = getWidth();
	//		programHeight = getHeight();
	//	}
	//}

}



void MainContentComponent::buttonClicked(Button *buttonThatWasClicked)
{

	if (buttonThatWasClicked == &zoomIn)
	{
		setFontSize(++fontSize);
	}
	else if (buttonThatWasClicked == &zoomOut)
	{
		setFontSize(--fontSize);
	}
	else if (buttonThatWasClicked == &fileChooser)
	{
		FileChooser myChooser("Select the text-based to read.",
			File::getSpecialLocation(File::userHomeDirectory),
			"*");
		if (myChooser.browseForFileToOpen())
		{
			filename = myChooser.getResult().getFullPathName();
		}
		setFilenameLabel();
	}
}

void MainContentComponent::setFontSize(int val) {
	fontSize = val;
	if (fontSize < 5) { fontSize = 5; }
	textBox.applyFontToAllText(Font(Font::getDefaultMonospacedFontName(), fontSize, Font::plain));
}

void MainContentComponent::setFilenameLabel()
{
	filenameLabel.setText(filename, sendNotificationAsync);
}

void MainContentComponent::writeSettingsFile()
{
	XmlElement programSettings("ProgramSettings");
	programSettings.setAttribute("filename", filename);
	programSettings.setAttribute("fontSize", fontSize);
	programSettings.setAttribute("autoScroll", autoScroll.getToggleState());
	programSettings.setAttribute("windowWidth", programWidth);
	programSettings.setAttribute("windowHeight", programHeight);
	programSettings.setAttribute("fullscreen", this->getPeer()->isFullScreen());
	programSettings.setAttribute("screenPosX", getScreenX());
	programSettings.setAttribute("screenPosY", getScreenY());

	String myXmlDoc = programSettings.createDocument(String());
	getSettingsFile().replaceWithText(myXmlDoc);
}



void MainContentComponent::readSettingsFile()
{
	if (getSettingsFile().exists())
	{
		ScopedPointer<XmlElement> xmlEle(XmlDocument::parse(getSettingsFile()));
		if (xmlEle->hasTagName("ProgramSettings"))
		{
			filename = xmlEle->getStringAttribute("filename");
			setFontSize(xmlEle->getIntAttribute("fontSize"));
			autoScroll.setToggleState(xmlEle->getBoolAttribute("autoScroll"), dontSendNotification);
			//programWidth = xmlEle->getIntAttribute("windowWidth");
			//programHeight = xmlEle->getIntAttribute("windowHeight");
			//setFullscreenFlag = xmlEle->getBoolAttribute("fullscreen");
			//boundsFromSettingsFile = Rectangle<int>(xmlEle->getIntAttribute("screenPosX"), xmlEle->getIntAttribute("screenPosY"), programWidth, programHeight);

		}
	}
	else 
	{
		DBG("SETTINGS FILE NOT FOUND.");
	}
	
}

File MainContentComponent::getSettingsFile()
{
	return (File (File::getCurrentWorkingDirectory().getFullPathName() + "\\LogFileReader.xml"));
}

inline const String MainContentComponent::boolToString(bool b)
{
	return b ? "true" : "false";
}