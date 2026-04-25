[Code]
function IsWindowsDarkMode: Boolean;
var
  regValue: Integer;
begin
  Result := False;
  if RegQueryDWordValue(HKCU, 
    'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize',
    'AppsUseLightTheme', regValue) then
  begin
    Result := (regValue = 0);
  end;
end;

procedure InitializeWizard;
begin
  if IsWindowsDarkMode then
  begin
    WizardImageFile := 'installer_graphics\abcs_wizard_dark.png';
    WizardSmallImageFile := 'installer_graphics\abcs_small_dark.png';
  end
  else
  begin
    WizardImageFile := 'installer_graphics\abcs_wizard_light.png';
    WizardSmallImageFile := 'installer_graphics\abcs_small_light.png';
  end;
end;
