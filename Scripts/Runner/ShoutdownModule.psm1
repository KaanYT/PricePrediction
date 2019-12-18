# Functions
function ShutDown-With-Popup {
    [CmdletBinding()]
    Param()
    
    $TimeOut = 30 
    # Load WPF assembly
    Add-Type -AssemblyName PresentationFramework

# Define WPF window
$window = [Windows.Markup.XamlReader]::Load(
    [Xml.XmlNodeReader]::new([xml]@'
    <Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
            xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
            xmlns:local="clr-namespace:RebootTimer"
            Title="Idle Reboot Alert" Height="195" Width="400" MaxHeight="195" MaxWidth="400" MinHeight="195" MinWidth="400" ShowInTaskbar="False" Topmost="True" WindowStartupLocation="CenterScreen" WindowStyle="ToolWindow">
        <Grid>
            <Grid.RowDefinitions>
                <RowDefinition></RowDefinition>
                <RowDefinition Height="30"></RowDefinition>
                <RowDefinition></RowDefinition>
            </Grid.RowDefinitions>
            <Grid.ColumnDefinitions>
                <ColumnDefinition></ColumnDefinition>
            </Grid.ColumnDefinitions>
            <TextBlock x:Name="AlertText" Grid.Row="0" FontSize="14" TextWrapping="Wrap" VerticalAlignment="Center" HorizontalAlignment="Center" TextAlignment="Center">
                <Run>You have exceeded the 10 min idle timeout.</Run>
                <LineBreak/>
                <Run>The system will restart in ...</Run>
            </TextBlock>
            <TextBlock x:Name="CountdownText" Grid.Row="1" FontSize="22" FontWeight="Bold" TextWrapping="Wrap" HorizontalAlignment="Center" VerticalAlignment="Center" TextAlignment="Center" />
            <Button x:Name="CancelButton" Grid.Row="2" Height="35" Width="75">Cancel</Button>
        </Grid>
    </Window>
'@)
)

    # Get controls to manipulate
    $countdownText = $window.FindName('CountdownText')
    $cancelButton = $window.FindName('CancelButton')

    # Add event handler to cancel button
    $cancelButton.Add_Click({$window.Close()})

    $window.Add_SourceInitialized({           
        $script:seconds = $TimeOut

        $countdownText.Text = "$($script:seconds)s"

        $script:timer = New-Object System.Windows.Threading.DispatcherTimer
        $script:timer.Interval = ([TimeSpan]'0:0:1.0') # Fire every second

        $script:timer.Add_Tick.Invoke({   
            $countdownText.Text = "$($script:seconds)s"

            if($script:seconds-- -le 0) {
               Stop-Computer -force
            }
        })

        $script:timer.Start()
    })

    # Show the window
    $window.ShowDialog() | Out-Null  
}
