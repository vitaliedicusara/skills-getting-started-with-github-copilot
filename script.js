document.addEventListener('DOMContentLoaded', () => {
    const activities = [
        {
            name: 'Hiking Trip',
            date: '2023-10-15',
            participants: ['Alice', 'Bob', 'Charlie']
        },
        {
            name: 'Cooking Class',
            date: '2023-10-20',
            participants: ['Dave', 'Eve']
        },
        {
            name: 'Yoga Session',
            date: '2023-10-25',
            participants: []
        }
    ];

    const activitiesContainer = document.querySelector('#activities-container');
    activities.forEach(activity => {
        const activityCard = renderActivityCard(activity);
        activitiesContainer.appendChild(activityCard);
    });
});

function renderActivityCard(activity) {
    const card = document.createElement('div');
    card.className = 'activity-card';

    const activityName = document.createElement('h3');
    activityName.textContent = activity.name;
    card.appendChild(activityName);

    const activityDate = document.createElement('p');
    activityDate.textContent = `Date: ${activity.date}`;
    card.appendChild(activityDate);

    // Add participants section
    const participantsSection = document.createElement('div');
    participantsSection.className = 'participants-section';

    const participantsTitle = document.createElement('h4');
    participantsTitle.textContent = 'Participants';
    participantsSection.appendChild(participantsTitle);

    const participantsList = document.createElement('ul');
    participantsList.className = 'participants-list';

    // Populate participants list
    if (activity.participants && activity.participants.length > 0) {
        activity.participants.forEach(participant => {
            const listItem = document.createElement('li');
            listItem.textContent = participant;
            participantsList.appendChild(listItem);
        });
    } else {
        const noParticipants = document.createElement('li');
        noParticipants.textContent = 'No participants yet.';
        participantsList.appendChild(noParticipants);
    }

    participantsSection.appendChild(participantsList);
    card.appendChild(participantsSection);

    return card;
}